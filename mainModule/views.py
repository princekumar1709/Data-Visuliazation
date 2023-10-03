from django.shortcuts import render,redirect
import pandas as pd
from .models import ExcelSheetData
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# Create your views here.

def homepage(request):
    items = [
        {
            "icon": "img/pie-chart.png",
            "title": "Pie Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/bar-chart.png",
            "title": "Bar Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/donut.png",
            "title": "Donut Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/histogram.png",
            "title": "Histogram Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/scatterPlot.png",
            "title": "ScatterPlot Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/gantt-chart.png",
            "title": "Gantt Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/area-graph.png",
            "title": "Area Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
        {
            "icon": "img/pyramid-chart.png",
            "title": "Pyramid Chart",
            "contents": "Reduce file size while optimizing for maximal PDF quality",
        },
    ]

    if request.method == "POST":
        title = request.POST.get("title")
        index_form = {"title": title}
        print("index_form:", index_form)
        request.session["index_form"] = index_form
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

            # Process the uploaded file as needed (e.g., read the data, compress, etc.)
            # For demonstration purposes, let's assume you just want to save the file to the 'media' folder.

            # Get the file's name
            df = pd.read_excel(uploaded_file, engine="openpyxl")
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

            # Here, you can process the uploaded file and return an appropriate response.
            # For example, you can return a success message to display on the web page.
        return redirect("/workpage")
    return render(request, "uploadfile.html", {"index_form": index_form})

@login_required
def workpage(request):
    try:
        all_objects = ExcelSheetData.objects.latest('created_at')
        data = all_objects.data
        data_json = json.dumps(data)
    except ExcelSheetData.DoesNotExist:
        data = []
    
    graphDetails = []

    if request.method == "POST":
        try:
            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)
            graphDetails = data.get("data")
            
            print(graphDetails)
            return JsonResponse(
                {"status": "success", "data": data,'data_json' : data_json, "graphDetails": graphDetails}
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format in the request."},
                status=400,
            )
    return render(request, "workpage.html", {"data": data,'data_json' : data_json, "graphDetails": graphDetails})



