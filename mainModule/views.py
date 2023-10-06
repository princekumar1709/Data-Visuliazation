from django.shortcuts import render,redirect
import pandas as pd
from .models import ExcelSheetData
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


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
        if "xls_file" in request.FILES:
            # Get the uploaded file from the request.FILES dictionary
            uploaded_file = request.FILES["xls_file"]
            # Get the file's name
            df = pd.read_excel(uploaded_file, engine="xlrd")
            data = df.to_dict(orient="records")
            all_keys = set().union(*data)
            print(all_keys)
            
            sortedData = {key: [] for key in all_keys}
            for item in data:
                for key in all_keys:
                    if key in item:
                        sortedData[key].append(item[key])
                    else:
                        sortedData[key].append(None)
            ExcelSheetInfo = ExcelSheetData.objects.create(data=sortedData)
            ExcelSheetInfo.save()

        return redirect("workpage")
    return render(request, "uploadfile.html", {"index_form": index_form})

@login_required
def workpage(request):
    try:
        all_objects = ExcelSheetData.objects.latest('created_at')
        print(all_objects)
        data = all_objects.data
        data_json = json.dumps(data)
        print(data_json)
    except ExcelSheetData.DoesNotExist:
        data = []
    
    graphDetails = []

    if request.method == "POST":
        try:
            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)
            #print(data)
            graphDetails = data.get("data")
            print('graphdetail :',graphDetails)
            return JsonResponse(
                {"status": "success", "data": data,'data_json' : data_json, "graphDetails": graphDetails}
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format in the request."},
                status=400,
            )
    return render(request, "workpage.html", {"data": data,'data_json' : data_json, "graphDetails": graphDetails})



