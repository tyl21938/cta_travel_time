'''
Convert Results Database to Python Dataframe for analysis
'''
cnx = sqlite3.connect("results.db")
results = pd.read_sql_query("SELECT * FROM results_travel_time", cnx)

results['median_tt'].describe()
results['quartile_tt'].describe()


'''
Output 'median_tt' histogram
**change column name field to get quartile histogram
'''
%matplotlib notebook
import matplotlib.pyplot as plt

axis = results.hist(column = 'median_tt', bins=100, grid=False, figsize=(12,8), color='#86bf91', zorder=2, rwidth=0.9)

axis = axis[0]
for x in axis:
    # Despine
    x.spines['right'].set_visible(False)
    x.spines['top'].set_visible(False)
    x.spines['left'].set_visible(True)

    # Switch off ticks
    x.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom=True, left=True, right=False, labelleft=True)

    # Draw horizontal axis lines
    vals = x.get_yticks()
    for tick in vals:
        x.axhline(y=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)

    # Rename Title
    x.set_title("ODX median travel times histogram")

    # Set x-axis label
    x.set_xlabel("Travel Time (Seconds)", labelpad=20, weight='bold', size=12)

    # Set y-axis label
    x.set_ylabel("Trips", labelpad=20, weight='bold', size=12)

plt.savefig('odx_medianTT_histogram.png', bbox_inches='tight')

#plt.show()
