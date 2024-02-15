from django.shortcuts import render, redirect
import pandas as pd
from .models import ExcelSheetData
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ydata_profiling import ProfileReport
import numpy as np
import plotly.express as px
import re

# Create your views here.
# @login_required
def homepage(request):
    items = [
        {
            "icon": "img/pie-chart.png",
            "title": "Pie Chart",
            "contents": "Useful for showing the composition of a dataset.",
        },
        {
            "icon": "img/bar-chart.png",
            "title": "Bar Chart",
            "contents": "Useful for comparing different categories or groups.",
        },
        {
            "icon": "img/histogram.png",
            "title": "Histogram Chart",
            "contents": "Useful to visualize data patterns and trends.",
        },
        {
            "icon": "img/scatterPlot.png",
            "title": "ScatterPlot Chart",
            "contents": "Useful for showing the relationship or correlation between two variables.",
        },
        {
            "icon": "img/donut.png",
            "title": "Donut Chart",
            "contents": "Useful for displaying the composition of a dataset.",
        },
        {
            "icon": "img/gantt-chart.png",
            "title": "Gantt Chart",
            "contents": "Useful in project management to schedule and visualize the timeline of tasks and activities.",
        },
        {
            "icon": "img/area-graph.png",
            "title": "Area Chart",
            "contents": "Useful for visualizing data such as sales, revenue, or population growth.",
        },
        {
            "icon": "img/pyramid-chart.png",
            "title": "Pyramid Chart",
            "contents": "Useful for visualizing population demographics or employee organizational structures.",
        },
    ]

    if request.method == "POST":
        # title = request.POST.get("title")
        # index_form = {"title": title}
        # print("index_form:", index_form)
        # request.session["index_form"] = index_form
        return redirect("uploadfile")

    return render(request, "homepage.html", {"items": items})


@login_required
def uploadfile(request):

    index_form = request.session.get("index_form")

    if request.method == "POST":
            # Check if the form contains the file input with the name "xls_file"
            if "xls_file" in request.FILES or "xlsx_file" in request.FILES:

                # Get the uploaded file from the request.FILES dictionary
                uploaded_file = request.FILES["xls_file"]
                # Get the file's name
                df = pd.read_excel(uploaded_file, engine="xlrd")

                if "view_data" in request.POST:
                # Render the 'data.html' template with the DataFrame
                    return render(request, 'data.html', {'df': df})
            
                if "see_report" in request.POST:
                    # Generate the profile report
                    report = ProfileReport(df, title='Profiling Report')
                    # Save the report to a file
                    report.to_file(output_file='static/Report.html')
                    # Redirect to the report page
                    return redirect("static/Report.html")
                
                if "generate_graphs" in request.POST:
                    df=df.dropna()
                    # Convert DataFrame to dictionary
                    data = df.to_dict(orient="records")
                    all_keys = set().union(*data)
                    sortedData = {key: [] for key in all_keys}
                    for item in data:
                        for key in all_keys:
                            sortedData[key].append(item.get(key))
                    # Create and save ExcelSheetData instance
                    ExcelSheetInfo = ExcelSheetData.objects.create(data=sortedData)
                    ExcelSheetInfo.save()
                    # Redirect to the workpage
                    return redirect("workpage")
            
            return render(request, 'error.html')
    
    return render(request, "uploadfile.html", {"index_form": index_form})


@login_required
def workpage(request):
    try:
        all_objects = ExcelSheetData.objects.latest('created_at')
        data = all_objects.data
        # fetching data from database
        data_json = json.dumps(data)
        # print(data_json)
    except ExcelSheetData.DoesNotExist:
        data = []

    graphDetails = {}

    if request.method == "POST":
        lis=[rq for rq in request.POST]
        print('lis  :', lis)
        try:
            body_unicode = request.body.decode("utf-8")
            print(body_unicode)
            data = json.loads(body_unicode)
            # draggable data
            graphDetails = data.get("data")
            desired_column = 'columns'
            desired_row = 'rows'

            column = getFilteredValue(graphDetails, desired_column)
            row = getFilteredValue(graphDetails, desired_row)
        
            if column is None or row is None:
                # Either column or row is not present; show a table instead
                if(column):
                    df=pd.DataFrame({column:json.loads(data_json)[column]})
                    if type(df[column][0]) in [np.float64,np.float32,np.int32,np.int64]:
                        if 'box' in request:
                            px.box(data_frame=df,x=column)
                        # if chartType=="kde":
                        #     px.box(data_frame=df,x=column)
                        else:
                            fig=px.histogram(data_frame=df,x=column,nbins=10,title='Distribution of %s'%(column))
                    else:
                        fig=px.bar(x=df[column].sort_values().unique(),y=df.groupby(column)[column].value_counts().values,color=df[column].unique(),text_auto=True,title='Distribution of %s'%(column))
                        fig.update_traces(width=0.4)
                        fig.update_layout(xaxis_title=column, yaxis_title='Counts')
                        
                else:
                    df=pd.DataFrame({row:json.loads(data_json)[row]})
                    if type(df[row][0]) in [np.float64,np.float32,np.int32,np.int64]:
                        fig=px.histogram(data_frame=df,x=row,nbins=10,title='Distribution of %s'%(row))
                        
                    else:
                        fig=px.bar(x=df[row].sort_values().unique(),y=df.groupby(row)[row].value_counts().values,color=df[row].unique(),text_auto=True,title='Distribution of %s'%(row))
                        fig.update_traces(width=0.4)
                        fig.update_layout(xaxis_title=row, yaxis_title='Counts')
                # fig.update_traces(width=0.4)   
                fig.write_html("static/plotly_graph.html",default_height=420)
                return JsonResponse(
                {"status": "success", "data": data, 'data_json': data_json,
                    "graphDetails": graphDetails,'plotly_graph_exists':plotly_graph_exists()}
            )
            # Create a DataFrame using the selected columns and data from data_json
            if column is not None and row is not None:
                df = pd.DataFrame({
                    column: json.loads(data_json)[column],
                    row: json.loads(data_json)[row],  # Example data, replace with your own
                    })
                if ((type(df[column][0]) in [np.float64,np.float32,np.int32,np.int64]) & (type(df[row][0]) in [np.float64,np.float32,np.int32,np.int64])):
                    fig=px.scatter(df,x=column,y=row,title='%s VS %s' %(column,row))

                elif((type(df[column][0]) in [str]) & (type(df[row][0]) in [np.float64,np.float32,np.int32,np.int64])):
                    fig=px.bar(df,x=df[column].sort_values().unique(),y=df.groupby(column)[row].sum().values,color=df[column].unique(),title='%s VS %s' %(column,row))
                    fig.update_traces(width=0.4)
                    fig.update_layout(xaxis_title=column, yaxis_title=row)

                elif((type(df[column][0]) in [np.float64,np.float32,np.int32,np.int64]) & (type(df[row][0]) in [str])):
                    fig=px.bar(df,x=df[row].sort_values().unique(),y=df.groupby(row)[column].sum().values,color=df[row].unique(),title='%s VS %s' %(row,column))
                    fig.update_traces(width=0.4)
                    fig.update_layout(xaxis_title=row, yaxis_title=column)
                else:
                    # fig=go.Figure(data=go.Heatmap(x=df[column] ,y=df[row]),z=data)
                    fig=px.bar(data_frame=df,x=df[column].unique(),y=df[column].value_counts().values,color=df[row].unique())

                fig.write_html("static/plotly_graph.html",default_height=420)

            # Generate an HTML representation of the Plotly figure
            # fig.show()

                return JsonResponse(
                    {"status": "success", "data": data, 'data_json': data_json,
                    "graphDetails": graphDetails,'plotly_graph_exists':plotly_graph_exists()}
                )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format in the request."},
                status=400,
            )
    return render(request, "workpage.html", {"data": data, 'data_json': data_json, "graphDetails": graphDetails,'plotly_graph_exists':plotly_graph_exists})



import os
def plotly_graph_exists():
    return os.path.exists("static/plotly_graph.html")


def getFilteredValue(graphDetails, desired_key):
    for item in graphDetails:
        if item['id'] == desired_key:
            return item['value']
    return None


def getFilteredArray(graphDetails, desired_key):
    for item in graphDetails:
        return item[desired_key]
    return []



def createTable(data_json_str, desired_key):
    try:
        # Create an HTML table from the provided data
        table_html = "<table border='1'>"
        
        table_html += "<tr>"
        table_html += "<th>" + desired_key + "</th>"
        table_html += "<th>Data</th>"
        table_html += "</tr>"
        
        # Parse the JSON string into a list of dictionaries
        
        table_html += "<tr>"
        table_html += "<td>" + desired_key + "</td>"
        table_html += "<td>" + json.dumps(unique(data_json_str)) + "</td>"
        table_html += "</tr>"
        table_html += "</table>"
        return table_html
    except json.JSONDecodeError:
        return "<p>Error: Invalid JSON data</p>"
    

def unique(list1):
 
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list



    
    
