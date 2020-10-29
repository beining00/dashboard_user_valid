import pandas as pd
from random import randint
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, DataTable, TableColumn,SelectEditor,CustomJS, Button,StringFormatter,NumberFormatter
from bokeh.layouts import column, layout, row
from bokeh.plotting import figure, curdoc
import copy
import calendar
import time


def get_timestamp():
    # get current time
    gmt = time.gmtime()
    ts = calendar.timegm(gmt)
    return ts


# define constance
OPTIONS = ['banana', 'apple', 'pear']
STATE = ["TODO", "DONE", "NOT DECIDED"]
N = 100
CHANGE_COLS = ['nmi', "col_changed", "old", "new", "timestamp"]

# create empty csv
(pd.DataFrame(columns= CHANGE_COLS)).to_csv("save.csv")

data = dict(
#         dates=[date(2014, 3, i+1) for i in range(100)],
        nmi =[randint(0, 100) for i in range(N)],
      prediction =[OPTIONS[randint(0, 2)] for i in range(N)],
        user_valid =["" for i in range(N)],
        progress = [ 'TODO' for i in range(N)]
    )

source = ColumnDataSource(data)
old_source = ColumnDataSource(copy.deepcopy(source.data))
# selectEditor

valid_selector = SelectEditor(options = OPTIONS)
state_selector = SelectEditor(options = STATE)




button = Button(label="Download", button_type="success")

button.js_on_click(CustomJS(args=dict(source=source),
                            code= '''
                console.log("test");
                function table_to_csv(source) {
                    const columns = Object.keys(source.data);
                    const nrows = source.get_length();
                    const lines = [columns.join(',')];
                    console.log(lines);  
                      for (let i = 0; i < nrows; i++) {
                            var row = [];
                            for (let j = 0; j < columns.length; j++) {
                                     const column = columns[j];
                                    row.push(source.data[column][i].toString());
                                }
                                lines.push(row.join(','));
                        }

                    var a = lines.join('\\n').concat('\\n');
                    //console.log(a);
                    return a;
                }
                const filename = 'data_result1.csv';
                const filetext = table_to_csv(source);
                const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });
                //addresses IE
                if (navigator.msSaveBlob) {
                    console.log("save");
                    navigator.msSaveBlob(blob, filename);
                } else {
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = filename;
                    link.target = '_blank';
                    link.style.visibility = 'hidden';
                    link.dispatchEvent(new MouseEvent('click'));
                    console.log("not save");

                }
                            '''))


columns = [
    TableColumn(field="nmi",
                title="nmi",
                formatter=StringFormatter(font_style="bold")),
    TableColumn(field="prediction",
                title="prediction") ,
    TableColumn(field="user_valid",
                title="user validation",
                editor=valid_selector) ,
    TableColumn(field="progress",
                title="progress",
                editor = state_selector)
]



data_table = DataTable(source=source, columns=columns, width=800 , height=400,editable = True)



#
# # create a callback that will save the operation
# def my_callback():
#     global i
#
#     i = 0
#     (pd.DataFrame(source.data)).to_csv("save" + str(i) + ".csv")
#     i += 1




def on_change_data_source(attr, old, new):
    # old, new and source.data are the same dictionaries
    #print('-- SOURCE DATA: {}'.format(source.data))
    #print('>> OLD SOURCE: {}'.format(old_source.data))

    # to check changes in the 'y' column:
    progress_change = [] # (nmi, old, new )
    user_valid_change = [] # (nmi , old, new )

    # change df
    change_df = pd.DataFrame(columns=CHANGE_COLS)


    for i in range(len(old_source.data['nmi'])):
        cur_nmi = old_source.data['nmi'][i]
        if old_source.data['progress'][i] != source.data['progress'][i]:
            # change
            progress_change.append((cur_nmi, old_source.data['progress'][i] , source.data['progress'][i]))

            # add to df
            change_df = change_df.append({'nmi' : cur_nmi, 'col_changed': 'progress', 'new': source.data['progress'][i]
                                , 'old' : old_source.data['progress'][i],
                                 'timestamp' : get_timestamp()}
                                ,ignore_index=True )


        if old_source.data['user_valid'][i] != source.data['user_valid'][i]:
            # change
            user_valid_change.append((cur_nmi, old_source.data['user_valid'][i], source.data['user_valid'][i]))
            # add to df
            change_df = change_df.append({'nmi': cur_nmi, 'col_changed': 'user_valid', 'new': source.data['user_valid'][i]
                                 , 'old': old_source.data['user_valid'][i],
                              'timestamp': get_timestamp()}
                             , ignore_index=True)


    #print('>> USER CHANGES: {}'.format(user_valid_change))
    #print('>> PROGRESS CHANGES: {}'.format(progress_change))

    old_source.data = dict(copy.deepcopy(source.data))
    #print(user_valid_change)
    #print(progress_change)
    print(change_df)
    change_df.to_csv('save.csv', mode='a', header=False)




data_table.source.on_change('data', on_change_data_source)

total = column(button, data_table)

curdoc().add_root(total)



