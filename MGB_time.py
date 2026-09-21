################time
import pandas as pd
from datetime import datetime
mask_mgb = df_final['source'] == 'MGB'
mask_others = ~mask_mgb
print("Initializing the global timezone-naive standard time axis...")

# Convert all original timestamps, remove all potential timezones (+00:00),
# and standardize the precision to seconds
df_final['order_time_jittered_std'] = (
    pd.to_datetime(df_final['order_time_jittered'], errors='coerce')
    .dt.tz_localize(None)  # Remove timezone information from all timestamps
    .dt.floor('s')
)
print("Processing linear stretching of MGB timestamps...")

def to_seconds_robust(val):
    if pd.isna(val):
        return None
    s = str(val).replace('T', ' ').replace('Z', '')[:19]
    try:
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timestamp()
    except ValueError:
        try:
            return datetime.strptime(s, '%Y-%m-%d').timestamp()
        except ValueError:
            return None

# Extract only MGB timestamps for Unix-second conversion
mgb_seconds = df_final.loc[mask_mgb, 'order_time_jittered'].apply(to_seconds_robust)
s_min = mgb_seconds.min()
s_max = mgb_seconds.max()

# Define the target mapping range (2015-2024)
target_min = datetime(2015, 1, 1).timestamp()
target_max = datetime(2024, 12, 31).timestamp()

print("Performing MGB linear mapping and replacement...")

if s_max != s_min:
    mgb_mapped_seconds = (mgb_seconds - s_min) / (s_max - s_min) * (target_max - target_min) + target_min

    # Fill the MGB positions with the mapped timestamps
    # Both sides are now timezone-naive datetime64[ns]
    df_final.loc[mask_mgb, 'order_time_jittered_std'] = (
        pd.to_datetime(mgb_mapped_seconds, unit='s')
        .dt.floor('s')
    )
else:
    df_final.loc[mask_mgb, 'order_time_jittered_std'] = pd.Timestamp('2015-01-01')

print("timestamp alignment completed successfully!")
