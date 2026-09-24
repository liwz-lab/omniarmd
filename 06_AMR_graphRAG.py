from datetime import datetime, timezone
import json
import logging
import os

from neo4j import GraphDatabase
from openai import OpenAI
import pandas as pd

os.environ["no_proxy"] = ""
os.environ["NO_PROXY"] = ""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Omni-ARMD-KnowledgeGraph")

NEO4J_URI = ""
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "secretgraph"

DATASET_PATH = ""
os.environ["OPENROUTER_API_KEY"] = ""
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "moonshotai/kimi-k2.5"


def safe_str(x):
    if pd.isna(x):
        return None
    x = str(x).strip()
    if x == "" or x.lower() in {"nan", "none", "null"}:
        return None
    return x


def safe_float(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def safe_bool(x):
    if pd.isna(x):
        return None
    if isinstance(x, bool):
        return x
    x = str(x).strip().lower()
    if x in {"true", "1", "yes"}:
        return True
    if x in {"false", "0", "no"}:
        return False
    return None


# =========================
# 3. Read and Clean knowledge_summary_valid
# =========================


def load_knowledge_summary(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path, low_memory=False)
    logger.info(f"Raw knowledge_summary shape: {df.shape}")

    required_cols = [
        "organism_std",
        "antimicrobial_std",
        "gene_symbol",
        "I",
        "R",
        "S",
        "total_I",
        "total_R",
        "total_S",
        "gene_total",
        "total_non_s",
        "gene_non_s",
        "total_all",
        "R_rate_among_gene_positive",
        "Non_S_rate_among_gene_positive",
        "gene_prevalence_in_R",
        "gene_prevalence_in_Non_S",
        "gene_prevalence_in_S",
        "log_odds_non_s_vs_s",
        "evidence_n",
        "GPAS",
        "evidence_level",
        "resistance_evidence_label",
        "resistance_evidence_label_cn",
        "valid",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in input table: {missing}")

    out = pd.DataFrame()

    out["organism_std"] = df["organism_std"].map(safe_str).str.lower()
    out["antimicrobial_std"] = df["antimicrobial_std"].map(safe_str).str.lower()
    out["gene_symbol"] = df["gene_symbol"].map(safe_str)

    numeric_cols = [
        "I",
        "R",
        "S",
        "total_I",
        "total_R",
        "total_S",
        "gene_total",
        "total_non_s",
        "gene_non_s",
        "total_all",
        "R_rate_among_gene_positive",
        "Non_S_rate_among_gene_positive",
        "gene_prevalence_in_R",
        "gene_prevalence_in_Non_S",
        "gene_prevalence_in_S",
        "log_odds_non_s_vs_s",
        "evidence_n",
        "GPAS",
        "resistance_evidence_label_cn",
        "valid",
    ]

    for col in numeric_cols:
        out[col] = df[col].map(safe_float)

    text_cols = [
        "evidence_level",
        "resistance_evidence_label",
        "resistance_evidence_label_cn",
    ]

    for col in text_cols:
        out[col] = df[col].map(safe_str)

    out["source_file"] = os.path.basename(path)
    out["loaded_at"] = datetime.now(timezone.utc).isoformat()

    out = out.dropna(
        subset=["organism_std", "antimicrobial_std", "gene_symbol"]
    ).copy()

    out = out.drop_duplicates(
        subset=["organism_std", "antimicrobial_std", "gene_symbol"]
    ).reset_index(drop=True)

    out["evidence_id"] = [
        f"OMNI_EVIDENCE_{i:08d}" for i in range(len(out))
    ]

    logger.info(f"Cleaned importable evidence shape: {out.shape}")

    return out


# =========================
# 4. Neo4j Schema
# =========================


def init_neo4j_schema(driver):
    cypher_list = [
        "CREATE CONSTRAINT gene_symbol IF NOT EXISTS FOR (g:Gene) REQUIRE g.symbol IS UNIQUE",
        "CREATE CONSTRAINT species_name IF NOT EXISTS FOR (s:Species) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT antibiotic_name IF NOT EXISTS FOR (a:Antibiotic) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT evidence_id IF NOT EXISTS FOR (e:Evidence) REQUIRE e.evidence_id IS UNIQUE",
        "CREATE INDEX evidence_GPAS IF NOT EXISTS FOR (e:Evidence) ON (e.GPAS)",
        "CREATE INDEX evidence_level IF NOT EXISTS FOR (e:Evidence) ON (e.evidence_level)",
        "CREATE INDEX evidence_label IF NOT EXISTS FOR (e:Evidence) ON (e.resistance_evidence_label)",
        "CREATE INDEX evidence_non_s_rate IF NOT EXISTS FOR (e:Evidence) ON (e.Non_S_rate_among_gene_positive)",
    ]

    with driver.session() as session:
        for cypher in cypher_list:
            session.run(cypher)

    logger.info("Neo4j schema initialization complete")


# =========================
# 5. Batch Import to Neo4j
# =========================


def import_batch(tx, records):
    cypher = """
    UNWIND $records AS row

    MERGE (g:Gene {symbol: row.gene_symbol})
      ON CREATE SET g.created_at = row.loaded_at

    MERGE (s:Species {name: row.organism_std})
      ON CREATE SET s.created_at = row.loaded_at

    MERGE (a:Antibiotic {name: row.antimicrobial_std})
      ON CREATE SET a.created_at = row.loaded_at

    MERGE (e:Evidence {evidence_id: row.evidence_id})
      SET e.I = row.I,
          e.R = row.R,
          e.S = row.S,
          e.total_I = row.total_I,
          e.total_R = row.total_R,
          e.total_S = row.total_S,
          e.gene_total = row.gene_total,
          e.total_non_s = row.total_non_s,
          e.gene_non_s = row.gene_non_s,
          e.total_all = row.total_all,
          e.R_rate_among_gene_positive = row.R_rate_among_gene_positive,
          e.Non_S_rate_among_gene_positive = row.Non_S_rate_among_gene_positive,
          e.gene_prevalence_in_R = row.gene_prevalence_in_R,
          e.gene_prevalence_in_Non_S = row.gene_prevalence_in_Non_S,
          e.gene_prevalence_in_S = row.gene_prevalence_in_S,
          e.log_odds_non_s_vs_s = row.log_odds_non_s_vs_s,
          e.evidence_n = row.evidence_n,
          e.GPAS = row.GPAS,
          e.evidence_level = row.evidence_level,
          e.resistance_evidence_label = row.resistance_evidence_label,
          e.resistance_evidence_label_cn = row.resistance_evidence_label_cn,
          e.source_file = row.source_file,
          e.loaded_at = row.loaded_at

    MERGE (g)-[:HAS_EVIDENCE]->(e)
    MERGE (e)-[:FOR_SPECIES]->(s)
    MERGE (e)-[:AGAINST_ANTIBIOTIC]->(a)

    MERGE (g)-[r:GENE_DRUG_EVIDENCE {
        species: row.organism_std,
        antibiotic: row.antimicrobial_std
    }]->(a)
      SET r.GPAS = row.GPAS,
          r.evidence_level = row.evidence_level,
          r.resistance_evidence_label = row.resistance_evidence_label,
          r.Non_S_rate_among_gene_positive = row.Non_S_rate_among_gene_positive,
          r.R_rate_among_gene_positive = row.R_rate_among_gene_positive,
          r.log_odds_non_s_vs_s = row.log_odds_non_s_vs_s
    """
    tx.run(cypher, records=records)


def import_to_neo4j(driver, df, batch_size=500):
    records = df.where(pd.notnull(df), None).to_dict("records")
    total = len(records)

    with driver.session() as session:
        for start in range(0, total, batch_size):
            batch = records[start : start + batch_size]
            session.execute_write(import_batch, batch)
            logger.info(f"Imported {min(start + batch_size, total)}/{total}")

    logger.info("All knowledge_summary evidence successfully imported into Neo4j")


# =========================
# 6. Retrieval Functions
# =========================


def query_species_antibiotic_evidence(driver, species, antibiotic, top_n=20):
    cypher = """
    MATCH (g:Gene)-[:HAS_EVIDENCE]->(e:Evidence)-[:FOR_SPECIES]->(s:Species),
          (e)-[:AGAINST_ANTIBIOTIC]->(a:Antibiotic)
    WHERE toLower(s.name) CONTAINS toLower($species)
      AND toLower(a.name) CONTAINS toLower($antibiotic)
    RETURN
      g.symbol AS gene_symbol,
      s.name AS species,
      a.name AS antibiotic,
      e.resistance_evidence_label AS resistance_evidence_label,
      e.resistance_evidence_label_cn AS resistance_evidence_label_cn,
      e.evidence_level AS evidence_level,
      e.R_rate_among_gene_positive AS R_rate_among_gene_positive,
      e.Non_S_rate_among_gene_positive AS Non_S_rate_among_gene_positive,
      e.gene_prevalence_in_R AS gene_prevalence_in_R,
      e.gene_prevalence_in_Non_S AS gene_prevalence_in_Non_S,
      e.gene_prevalence_in_S AS gene_prevalence_in_S,
      e.log_odds_non_s_vs_s AS log_odds_non_s_vs_s,
      e.evidence_n AS evidence_n,
      e.GPAS AS GPAS,
      e.source_file AS source_file
    ORDER BY e.GPAS DESC
    LIMIT $top_n
    """

    with driver.session() as session:
        result = session.run(
            cypher,
            species=species,
            antibiotic=antibiotic,
            top_n=top_n,
        )
        return [dict(record) for record in result]


def query_gene_evidence(driver, gene_symbol, top_n=20):
    cypher = """
    MATCH (g:Gene)-[:HAS_EVIDENCE]->(e:Evidence)-[:FOR_SPECIES]->(s:Species),
          (e)-[:AGAINST_ANTIBIOTIC]->(a:Antibiotic)
    WHERE toLower(g.symbol) = toLower($gene_symbol)
    RETURN
      g.symbol AS gene_symbol,
      s.name AS species,
      a.name AS antibiotic,
      e.resistance_evidence_label AS resistance_evidence_label,
      e.evidence_level AS evidence_level,
      e.Non_S_rate_among_gene_positive AS Non_S_rate_among_gene_positive,
      e.log_odds_non_s_vs_s AS log_odds_non_s_vs_s,
      e.evidence_n AS evidence_n,
      e.GPAS AS GPAS
    ORDER BY abs(e.GPAS) DESC
    LIMIT $top_n
    """

    with driver.session() as session:
        result = session.run(
            cypher,
            gene_symbol=gene_symbol,
            top_n=top_n,
        )
        return [dict(record) for record in result]


# =========================
# 7. LLM Answer Generation
# =========================


def generate_rag_answer(query, evidence_rows):
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Please execute: export OPENROUTER_API_KEY='your_key'"
        )

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )

    context = json.dumps(
        evidence_rows,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are an expert bioinformatician tracking antimicrobial resistance.

Answer strictly based on the retrieved Omni-ARMD structured evidence.
Explain resistance or susceptibility direction using:
- resistance_evidence_label_cn
- resistance_evidence_label
- R_rate_among_gene_positive
- Non_S_rate_among_gene_positive
- log_odds_non_s_vs_s
- evidence_n
- GPAS
- evidence_level

Do not invent mechanisms or citations not present in the context.

[Retrieved Evidence]
{context}

[User Query]
{query}

[Answer]
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a careful AMR knowledgebase assistant. Use only provided structured evidence.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


# =========================
# 8. Main Workflow
# =========================


def main():
    df = load_knowledge_summary(DATASET_PATH)

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
        max_connection_lifetime=300,
        connection_timeout=60,
    )

    try:
        init_neo4j_schema(driver)

        import_to_neo4j(
            driver=driver,
            df=df,
            batch_size=500,
        )

        species = "acinetobacter baumannii"
        antibiotic = "amikacin"

        evidence_rows = query_species_antibiotic_evidence(
            driver=driver,
            species=species,
            antibiotic=antibiotic,
            top_n=20,
        )

        print("\n================ Retrieved Evidence ================")
        for row in evidence_rows:
            print(row)

        if not evidence_rows:
            print(
                "\nNo relevant evidence found. Please check whether organism_std / antimicrobial_std matches."
            )
            return

        scientific_query = (
            f"Which genes in {species} are associated with {antibiotic} "
            f"resistance or susceptibility based on Omni-ARMD final scores?"
        )

        answer = generate_rag_answer(
            query=scientific_query,
            evidence_rows=evidence_rows,
        )

        print("\n================ LLM Answer ================")
        print(answer)

        output_file_path = "./AMR_RAG_Final_Report_deidentification.txt"
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("=== Omni-ARMD Graph-RAG Report ===\n")
            f.write(f"Query: {scientific_query}\n\n")
            f.write(answer)

        print(f"\nReport saved: {output_file_path}")

    finally:
        driver.close()
        print("\nNeo4j connection closed")


if __name__ == "__main__":
    main()
