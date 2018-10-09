from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views import generic
# Create your views here.
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from .models import Reports,Project,Subproject,datesofmonth
from .forms import ReportForm,ReportFormup
import xlwt,time,datetime,json
from django.http.response import HttpResponseRedirect
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum


class SignUp(generic.CreateView):

    form_class    = CustomUserCreationForm
    success_url   = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
def HomePageView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('reports')
    else:
        return HttpResponseRedirect('login')
    
class UserList(generic.ListView):
    context_object_name = 'emp_list'   # your own name for the list as a template variable
    queryset = CustomUser.objects.all()#filter(Empid='2002')[:5] # Get 5 books containing the title war
    template_name = 'users/usrlist.html'
    
def save_report_form(request, form, template_name):
    data1 = Project.objects.all()
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            reports = Reports.objects.filter(Empid=request.user.Empid,dtcollected=datetime.date.today()).order_by('Report_date')
            time.sleep(1)
            data['html_report_list'] = render_to_string('report/includes/partial_report_list.html', {
                'reports': reports
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form,'data':data1}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
def valuecheck(request):
    if request.POST['No_count']=='':
        request.POST = request.POST.copy()
        request.POST['No_count']=0
    if request.POST['No_hours']=='':
        request.POST = request.POST.copy()
        request.POST['No_hours']=0
    if str(request.POST['Attendence'])== "Permission":
        request.POST = request.POST.copy()
        request.POST['No_count']=0
        request.POST['Task'] =''
        request.POST['Project_name'] =None
        request.POST['Subproject_name'] =None
    elif str(request.POST['Attendence'])!= "Present":
        request.POST = request.POST.copy()
        request.POST['No_count']=0
        request.POST['No_hours']=0
        request.POST['Task'] =''
        request.POST['Project_name'] = None
        request.POST['Subproject_name'] = None
    return request
def pendingdate(request,empid):
    reportsdate = Reports.objects.values('Report_date').filter(Empid=empid)
    daterange = datesofmonth.objects.exclude(weekday__in = reportsdate)
    missdates  = daterange.filter(weekday__range=(datetime.date.today().replace(day=1),datetime.date.today()))
    newdict  = {}
    some_day_last_week = timezone.now().date() - timedelta(days=7)
#     monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
#     print(monday_of_last_week)
#     monday_of_this_week = monday_of_last_week + timedelta(days=7)
#     print(monday_of_this_week)
    datadict =  Reports.objects.filter(Empid=empid,Report_date__range=[some_day_last_week,datetime.date.today()])#,created_at__Report_date=monday_of_last_week, created_at__Report_date=monday_of_this_week)
    datadict = serializers.serialize("json", datadict)
    for fields in json.loads(datadict):
        if (str(fields['fields']['Report_date'])) in newdict:
            newdict[str(fields['fields']['Report_date'])].append(fields['fields'])
        else:
            newdict[str(fields['fields']['Report_date'])] = [fields['fields']]
    newdict = sorted(newdict.items())
    return newdict,missdates

def reportList(request):
    if request.user.is_authenticated:
        empid=request.user.Empid
        reports = Reports.objects.filter(Empid=request.user.Empid,dtcollected=datetime.date.today()).order_by('Report_date')
        newdict,missdates = pendingdate(request,empid)
        hours =  Reports.objects.filter(Empid=request.user.Empid,Report_date=datetime.date.today()).aggregate(Sum('No_hours'))
        if (hours['No_hours__sum']!=None):
            hr    = str(hours['No_hours__sum']).split('.')
            pending = datetime.timedelta(hours = int(hr[0]), minutes=int(hr[1]))
            if datetime.datetime.strptime(str(pending),'%H:%M:%S') < datetime.datetime.strptime('8:00:00','%H:%M:%S'):
                totasubmitedHRS = datetime.datetime.strptime(str(pending),'%H:%M:%S')
                total_defautHRS = datetime.datetime.strptime('8:00:00','%H:%M:%S')
                pending_hrs = total_defautHRS-totasubmitedHRS
            else:
                pending_hrs = '00:00:00'
        else:
                pending_hrs = '08:00:00'
        return render(request,'report/report_list.html', {'reports': reports,'dates':missdates,'Hours':str(pending_hrs)})    
    else:
        return redirect("home")
def report_create(request):
    if request.method == 'POST':
        request = valuecheck(request)
        form = ReportForm(request.POST)
    else:
        form = ReportForm()
    return save_report_form(request, form, 'report/includes/partial_report_create.html')

def report_update(request, pk):
    report = get_object_or_404(Reports, pk=pk)
    if request.method == 'POST':
        request = valuecheck(request)
        form = ReportFormup(request.POST, instance=report)
    else:
        form = ReportFormup(instance=report)
    return save_report_form(request, form, 'report/includes/partial_report_update.html')

def report_delete(request, pk):
    report = get_object_or_404(Reports, pk=pk)
    data = dict()
    if request.method == 'POST':
        report.delete()
        data['form_is_valid'] = True 
        reports = Reports.objects.filter(Empid=request.user.Empid,dtcollected=datetime.date.today()).order_by('Report_date')
        data['html_report_list'] = render_to_string('report/includes/partial_report_list.html', {
            'reports': reports
        })
    else:
        context = {'reports': report}
        data['html_form'] = render_to_string('report/includes/partial_report_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)

def load_subpro(request):
    project_id = request.GET.get('Project_name')
    subpro = Subproject.objects.filter(Project_name=project_id).order_by('Subproject_name')
    return render(request, 'hr/subpro_dropdown_list.html', {'data': subpro})


def reportlist(request):
    print(request.POST)
    empid = request.user.Empid
    newdict,missdates = pendingdate(request,empid)
    return render(request, "report/reportlist.html", {'form': newdict, 'dates' : missdates})

def reportlist_emp(request,eid):
    newdict,missdates = pendingdate(request,eid)
    return render(request, "report/reportlist.html", {'form': newdict, 'dates' : missdates})


def export_users_xls(request):
    if request.method=="POST":
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Reports.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Reports')
        # Sheet header, first row
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments' ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        month = request.POST['month']
        if str(month)!='':
            rows = Reports.objects.filter(Report_date__month=int(month)).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
            if len(rows) ==0:
                return HttpResponse("No reports for Selected Month")
        else:
            rows = Reports.objects.filter(Report_date__range=[request.POST['start_date'],request.POST['end_date']]).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
            if len(rows) ==0:
                return HttpResponse("No reports for Selected Month")
        for row in rows:
            lt = list(row)
            lt[3]=str(row[3])
            if row[5]!=None:
                lt[5]=str(Project.objects.get(id=int(row[5])))
            if row[6]!=None:
                lt[6]=str(Subproject.objects.get(id=int(row[6])))
            row = tuple(lt)
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        return response
    else:
        return render(request, 'report/export_report.html')
    
    
    
    
    
    
    
    
    
    