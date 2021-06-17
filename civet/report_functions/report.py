import json
import csv
from mako.template import Template
from mako.lookup import TemplateLookup
import datetime as dt
from civet import __version__
from civet.report_functions import timeline_functions

from mako.template import Template
from mako.runtime import Context
from mako.exceptions import RichTraceback
from io import StringIO
import os


def process_catchments():

    #output is list of catchment IDs

    #dict of 
    #catchment_id: catchment_1
    #treeString: newick_string

    return catchment_list, tree_strings

def make_query_summary_data(metadata, config):
    query_summary_data = []
    with open(metadata, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            table_row = {}
            for col in config["table_content"]:
                table_row[col] = row[col]
                
            query_summary_data.append(table_row)
    
    return query_summary_data

def make_fasta_summary_data(metadata,config):

    fasta_summary_data = []
    with open(metadata, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["source"] == "input_fasta":
                table_row = {}
                for col in config["fasta_table_content"]:
                    table_row[col] = row[col]
                    
                fasta_summary_data.append(table_row)
    
    return fasta_summary_data

def make_catchment_summary_data(metadata):

    return catchment_summary_data


def get_timeline(config):

    timeline_json = timeline_functions.make_timeline_json(config)

    with open(timeline_json,'r') as f:
        timeline_data = json.load(f)

    timeline_functions.make_timeline_colours(config)
    
    return timeline_data


def define_report_content(metadata,catchments,config):
    report_content = config["report_content"]

    data_for_report = {}
    if '1' in report_content:
        data_for_report["query_summary_data"] = make_query_summary_data(metadata, config)
        data_for_report["fasta_summary_data"] = make_fasta_summary_data(metadata, config)
    else:
        data_for_report["query_summary_data"] = ""
        data_for_report["fasta_summary_data"] = ""
    
    if '2' in report_content:
        data_for_report["catchment_data"] = ""
    else:
        data_for_report["catchment_data"] = ""

    if '3' in report_content:
        data_for_report["catchment_tree"] = ""
    else:
        data_for_report["catchment_tree"] = ""
    
    if '4' in report_content:
        data_for_report["catchment_snipit"] = ""
    else:
        data_for_report["catchment_snipit"] = ""

    if '5' in report_content:
        data_for_report["timeline_data"] = get_timeline(config)
    else:
        data_for_report["timeline_data"] = ""
    
    if '6' in report_content:
        data_for_report["map_background"] = ""
    else:
        data_for_report["map_background"] = ""
    
    if '7' in report_content:
        data_for_report["map_queries"] = ""
    else:
        data_for_report["map_queries"] = ""
    
    return data_for_report



def make_report(metadata,report_to_generate,config):
    #need to call this multiple times if there are multiple reports wanted

    catchments = [f"catchment_{i}" for i in range(1,config["catchment_count"]+1)]

    data_for_report = define_report_content(metadata,catchments,config)

    date = dt.datetime.today()
    
    template_dir = os.path.abspath(os.path.dirname(config["report_template"]))
    mylookup = TemplateLookup(directories=[template_dir]) #absolute or relative works

    mytemplate = Template(filename=config["report_template"], lookup=mylookup)
    buf = StringIO()

    ctx = Context(buf, 
                    date = date, 
                    version = __version__, 
                    catchments = catchments, 
                    query_summary_data = data_for_report["query_summary_data"],
                    fasta_summary_data = data_for_report["fasta_summary_data"],
                    timeline_data = data_for_report["timeline_data"],
                    config=config)

    try:
        mytemplate.render_context(ctx)
    except:
        traceback = RichTraceback()
        for (filename, lineno, function, line) in traceback.traceback:
            print("File %s, line %s, in %s" % (filename, lineno, function))
            print(line, "\n")
        print("%s: %s" % (str(traceback.error.__class__.__name__), traceback.error))

    with open(report_to_generate, 'w') as fw:
        fw.write(buf.getvalue())
    
