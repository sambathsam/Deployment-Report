from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import generic
# Create your views here.
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from .models import Reports,Project,Subproject,datesofmonth,Review
from .forms import ReportForm,ReportFormup,ReviewForm
from xlwt import *
import xlwt
import datetime,json
from django.http.response import HttpResponseRedirect
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.db.models import Q
        
def review(request,eid):
    if request.user.is_authenticated:
        result_set = get_object_or_404(CustomUser, Empid=eid)
        if request.method =="POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('userlist')
            else:
                print("invalid")
        else:
            form = ReviewForm()
        return render(request, 'review/review.html',{'form':form,'data':result_set})
    
class SignUp(generic.CreateView):
    form_class    = CustomUserCreationForm
    success_url   = reverse_lazy('userlist')
    template_name = 'registration/signup.html'
    
def HomePageView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('reports')
    else:
        return HttpResponseRedirect('login')
    
class UserList(generic.ListView):
    context_object_name = 'emp_list'   
    queryset = CustomUser.objects.all()
    template_name = 'users/usrlist.html'
    
def save_report_form(request, form, template_name):
    data1 = Project.objects.all()
    data  = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid']    = True
            reports = Reports.objects.filter(Empid=request.user.Empid,dtcollected=datetime.date.today()).order_by('Report_date')
            data['html_report_list'] = render_to_string('report/includes/partial_report_list.html', {
                'reports': reports
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form,'data':data1}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def valuecheck(request,hours):
    hour_issue = False
    rp_hr = str(request.POST['No_hours']).split('.')
    if hours['No_hours__sum'] ==None:
        db_hr = 0
        total_hours = int(db_hr)+int(rp_hr[0])
    else:
        db_hr = str(hours['No_hours__sum']).split('.')
        a  = 0
        if len(rp_hr) ==2:
            a = int(rp_hr[1])/60
        total_hours = int(db_hr[0])+int(rp_hr[0])+a
    if (total_hours>=24):
        hour_issue = True
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
    elif (str(request.POST['Attendence'])!= "Present") and (str(request.POST['Attendence'])!= "OT") and (str(request.POST['Attendence'])!= "WFH") and (str(request.POST['Attendence'])!= "HWFH") and (str(request.POST['Attendence'])!= "OTH"):
        request.POST = request.POST.copy()
        request.POST['No_count']=0
        request.POST['No_hours']=0
        request.POST['Task'] =''
        request.POST['Project_name'] = None
        request.POST['Subproject_name'] = None
    return request,hour_issue

def pendingdate(request,empid):
    reportsdate = Reports.objects.values('Report_date').filter(Empid=empid)
    daterange = datesofmonth.objects.exclude(weekday__in = reportsdate)
    tbl_first = datesofmonth.objects.values('weekday').order_by('weekday')[0]
    missdates = daterange.filter(weekday__range=(tbl_first['weekday'],datetime.date.today()))
    newdict  = {}
    some_day_last_week = timezone.now().date() - timedelta(days=7)
    datadict =  Reports.objects.filter(Empid=empid,Report_date__range=[some_day_last_week,datetime.date.today()])#,created_at__Report_date=monday_of_last_week, created_at__Report_date=monday_of_this_week)
    datadict = serializers.serialize("json", datadict)
    for fields in json.loads(datadict):
        if (str(fields['fields']['Report_date'])) in newdict:
            newdict[str(fields['fields']['Report_date'])].append(fields['fields'])
        else:
            newdict[str(fields['fields']['Report_date'])] = [fields['fields']]
    newdict = sorted(newdict.items())
    return newdict,missdates

def edit_report(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            if (request.POST['show_date']) !='':
                reports = Reports.objects.filter(Empid=request.user.Empid,Report_date=request.POST['show_date'])
                return render(request,'report/edit_report.html', {'reports': reports})
            else:
                return HttpResponse("<h2> Please select date before search")
        else:
            return render(request,'report/edit_report.html',{})
    else:
        return redirect("login")
    
def reviewlist(request):
    if request.user.is_authenticated:
        empid=request.user.Empid
        review_dict = {}
        datadict =  Review.objects.filter(EmpID=empid)#,created_at__Report_date=monday_of_last_week, created_at__Report_date=monday_of_this_week)
        datadict = serializers.serialize("json", datadict)
        for fields in json.loads(datadict):
            if (str(fields['fields']['dtcollected'])) in review_dict:
                review_dict[str(fields['fields']['dtcollected'])].append(fields['fields'])
            else:
                review_dict[str(fields['fields']['dtcollected'])] = [fields['fields']]
        review_dict = sorted(review_dict.items())
        newdict,missdates = pendingdate(request,empid)
        return render(request, "review/reviewlist.html", {'form': review_dict, 'dates' : missdates})
    
def reviewlist_emp(request,eid):
    if request.user.is_superuser:
        review_dict = {}
        datadict =  Review.objects.filter(EmpID=eid)#,created_at__Report_date=monday_of_last_week, created_at__Report_date=monday_of_this_week)
        datadict = serializers.serialize("json", datadict)
        for fields in json.loads(datadict):
            if (str(fields['fields']['dtcollected'])) in review_dict:
                review_dict[str(fields['fields']['dtcollected'])].append(fields['fields'])
            else:
                review_dict[str(fields['fields']['dtcollected'])] = [fields['fields']]
        review_dict = sorted(review_dict.items())
        newdict,missdates = pendingdate(request,eid)
        uname = get_object_or_404(CustomUser, Empid=eid)
        return render(request, "review/reviewlist.html", {'form': review_dict, 'dates' : missdates,'usrname':uname})
    else:
        return HttpResponse("<h3>Your are not Superuser</h3>")
def reportList(request):
    if request.user.is_authenticated:
        empid=request.user.Empid
        reports = Reports.objects.filter(Empid=request.user.Empid,dtcollected=datetime.date.today()).order_by('Report_date')
        newdict,missdates = pendingdate(request,empid)
        hours =  Reports.objects.filter(Empid=request.user.Empid,Report_date=datetime.date.today()).aggregate(Sum('No_hours'))
        if (hours['No_hours__sum']!=None):
            hr    = str(hours['No_hours__sum']).split('.')
            print(hr)
            if len(hr) ==2:
                pending = datetime.timedelta(hours = int(hr[0]), minutes=int(hr[1]))
            else:
                pending = datetime.timedelta(hours = int(hr[0]))
            print(pending)
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
        hours =  Reports.objects.filter(Empid=request.user.Empid,Report_date=datetime.date.today()).aggregate(Sum('No_hours'))
        request,hr_issue = valuecheck(request,hours)
        if hr_issue:
            messages.warning(request, 'Number of Hours Exceed More than 24.')
            form = ReportForm()
        else:
            form = ReportForm(request.POST)
    else:
        form = ReportForm()
    return save_report_form(request, form, 'report/includes/partial_report_create.html')

def report_update(request, pk):
    report = get_object_or_404(Reports, pk=pk)
    if request.method == 'POST':
        hours =  Reports.objects.filter(~Q(id = pk),Empid=request.user.Empid,Report_date=datetime.date.today()).aggregate(Sum('No_hours'))
        request,hr_issue = valuecheck(request,hours)
        if hr_issue:
            messages.warning(request, 'Hours Exceed More than 24.')
            form = ReportFormup(instance=report)
        else:
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
    if request.user.is_authenticated:
        empid = request.user.Empid
        newdict,missdates = pendingdate(request,empid)
        if request.method=='POST':
            newdict = {}
            if str(request.POST['show_date']) != '':
                datadict = Reports.objects.filter(Empid=request.user.Empid,Report_date=request.POST['show_date'])
                datadict = serializers.serialize("json", datadict)
                for fields in json.loads(datadict):
                    if (str(fields['fields']['Report_date'])) in newdict:
                        newdict[str(fields['fields']['Report_date'])].append(fields['fields'])
                    else:
                        newdict[str(fields['fields']['Report_date'])] = [fields['fields']]
                newdict = sorted(newdict.items())
                return render(request, "report/reportlist.html", {'form': newdict, 'dates' : missdates})
            else:
                return HttpResponse ("<h2>Please select the date before Click Search Button</h2><br><h4> Reload current page</h4>")
        else:
            return render(request, "report/reportlist.html", {'form': newdict, 'dates' : missdates})
    else:
        return redirect('login')
    
def reportlist_emp(request,eid):
    if request.user.is_superuser:
        newdict,missdates = pendingdate(request,eid)
        uname = get_object_or_404(CustomUser, Empid=eid)
        if request.method=='POST':
            newdict = {}
            if str(request.POST['show_date']) != '':
                datadict = Reports.objects.filter(Empid=eid,Report_date=request.POST['show_date'])
                datadict = serializers.serialize("json", datadict)
                for fields in json.loads(datadict):
                    if (str(fields['fields']['Report_date'])) in newdict:
                        newdict[str(fields['fields']['Report_date'])].append(fields['fields'])
                    else:
                        newdict[str(fields['fields']['Report_date'])] = [fields['fields']]
                newdict = sorted(newdict.items())
                return render(request, "report/reportlist.html", {'form': newdict, 'dates' : missdates,'usrname':uname})
            else:
                return HttpResponse ("<h2>Please select the date before Click Search Button</h2><br><h4> Reload current page</h4>")
        else:
            return render(request, "report/reportlist.html", {'form': newdict, 'dates' : missdates,'usrname':uname})
    else:
        return HttpResponse("<h3>Your are not Superuser</h3>")
def edit_user(request,eid):
    if request.user.is_authenticated:
        result_set = get_object_or_404(CustomUser, Empid=eid)
        if request.method =="POST":
            form = CustomUserCreationForm(request.POST, instance=result_set)
            if form.is_valid():
                form.save()
                return redirect('userlist')
            else:
                print("invalid")
    #     result_set = CustomUser.objects.filter(Empid=eid)
        form = CustomUserCreationForm(instance=result_set)
        return render(request, 'users/edit_user.html',{'form':form})
    
def attendence(request):
    if request.user.is_superuser:
        import calendar
        if request.method =="POST":
            month = request.POST['Month']
            if month == '':
                return HttpResponse('<h2> Please Select the Month</h2>')
            a= {};i=1
            Name_detail = CustomUser.objects.filter(~Q(Empid = 1)).values_list('Empid','EmpName')
            for name in Name_detail:
                name = name[1]
                a[name.lower()] = i
                i+=1
            currmonth = datetime.date.today().strftime('%Y-%m')
            year  = currmonth.split('-')[0]
            num_days = calendar.monthrange(int(year), int(month))[1]
            days = [datetime.date(int(year),int(month), day) for day in range(1, num_days+1)]
            rows = Reports.objects.filter(~Q(Empid = 1),Report_date__month=int(month)).values_list('Empid','Name','Report_date','Attendence').order_by('Empid')
            if len(rows)==0:
                return HttpResponse("<h2>No reports for Selected Month</h2>")
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Attendence.xls"'
            wb = xlwt.Workbook(encoding='utf-8');ws = wb.add_sheet('Attendence',cell_overwrite_ok=True)
            # Sheet header, first row
            row_num = 0;font_style = xlwt.XFStyle();font_style.font.bold = True
            aday = ['Empid','Name']
            for da_t in days:
                aday.append(str(da_t))
            aday.append('P');aday.append('EL');aday.append('HEL');aday.append('WFH')
            columns = aday
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()
            for row in Name_detail:
                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)
            atten = {'Present':'P','Leave':'EL','Half day leave':'HEL','WO':'WO','OT':'OT','Permission':'P','GH':'GH','WFH':'WFH','HWFH':'HWFH','OTH':'OTH'}
            name_mat = '';date_mat = '';atte_mat = ''
            Mday = [str(da_t) for da_t in days]
            arr_date = []
            for M_week in Mday:
                day_ = datetime.datetime.strptime(str(M_week),'%Y-%m-%d').strftime('%a')
                if str(day_) =='Sun' or str(day_) =='Sat':
                    arr_date.append(M_week)
            for row in rows:
                Name_r = row[1];date_r = row[2];atte_r = atten[str(row[3])]
                if Name_r !=name_mat:
                    for c in ['P','EL','HEL','WFH']:
                        ws.write(row_num, aday.index(str(c)), xlwt.Formula('COUNTIF(C'+str(row_num+1)+':AG'+str(row_num+1)+',"'+str(c)+'")'))
                    for wend in arr_date:
                        row_num = int(a[str(Name_r.lower())]);col_num = aday.index(str(wend))
                        ws.write(row_num, col_num, 'WO', font_style)
                if Name_r ==name_mat and date_mat == date_r:
                    if atte_r=='P' and atte_mat=='HEL':
                        atte_r = 'HEL'
                row_num = int(a[str(Name_r.lower())]);col_num = aday.index(str(date_r))
                ws.write(row_num, col_num, atte_r, font_style)
                name_mat = Name_r;date_mat = date_r;atte_mat = atte_r
            for c in ['P','EL','HEL','WFH']:
                ws.write(row_num, aday.index(str(c)), xlwt.Formula('COUNTIF(C'+str(row_num+1)+':AG'+str(row_num+1)+',"'+str(c)+'")'))
            wb.save(response)
            return response
        else:
            return render(request, 'review/Attendence.html')
    else:
        return HttpResponse("<h3>Your are not Superuser</h3>")

def export_users_xls(request):
    if request.user.is_superuser:
        if request.method=="POST":
            project_re = request.POST['Project_name'];subpro_re  = request.POST['Subproject_name']
            if str(project_re)!='' or str(subpro_re)!='' or str(request.POST['start_date'])!='' or request.POST['end_date'] != '':
                if str(project_re)!='' and str(subpro_re)!='' and  str(request.POST['start_date'])!='' and request.POST['end_date'] != '':
                    rows = Reports.objects.filter(Project_name=project_re,Subproject_name=subpro_re,Report_date__range=[request.POST['start_date'],request.POST['end_date']]).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                elif str(project_re)!='' and str(subpro_re)=='' and  str(request.POST['start_date'])!='' and request.POST['end_date'] != '':
                    rows = Reports.objects.filter(Project_name=project_re,Report_date__range=[request.POST['start_date'],request.POST['end_date']]).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                elif str(project_re)=='' and str(subpro_re)=='' and  str(request.POST['start_date'])!='' and str(request.POST['end_date']) != '':
                    rows = Reports.objects.filter(Report_date__range=[request.POST['start_date'],request.POST['end_date']]).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                elif str(project_re)=='' and str(subpro_re)!='' and  str(request.POST['start_date'])!='' and request.POST['end_date'] != '':
                    rows = Reports.objects.filter(Subproject_name=subpro_re,Report_date__range=[request.POST['start_date'],request.POST['end_date']]).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                elif str(project_re)!='' and str(subpro_re)!='' and  str(request.POST['start_date']) =='' and request.POST['end_date'] == '':
                    rows = Reports.objects.filter(Project_name=project_re,Subproject_name=subpro_re).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                elif str(project_re)!='' and str(subpro_re)=='' and  str(request.POST['start_date']) =='' and request.POST['end_date'] == '':
                    rows = Reports.objects.filter(Project_name=project_re).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                elif str(project_re)=='' and str(subpro_re)!='' and  str(request.POST['start_date']) =='' and request.POST['end_date'] == '':
                    rows = Reports.objects.filter(Subproject_name=subpro_re).values_list('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments').order_by('Empid')
                else:
                    return HttpResponse("<h2>Please Select Dates Correctly</h2>")
                if len(rows)==0:
                    return HttpResponse("<h2>No reports for Selected Dates</h2>")
            else:
                return HttpResponse("<h2>Please select Project Or Dates</h2><br><h2>Reload current Page</h2>")
            
            response = HttpResponse(content_type='application/ms-excel')
            if str(request.POST['start_date']) !='':
                response['Content-Disposition'] = 'attachment; filename="Reports_'+str(str(request.POST['start_date']))+'.xls"'
            else:
                response['Content-Disposition'] = 'attachment; filename="Reports.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Reports')
            # Sheet header, first row
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()
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
            pro = Project.objects.all()
            sub_pro = Subproject.objects.all()
            return render(request, 'report/export_report.html',{'pro':pro,'spro':sub_pro})
    else:
        return HttpResponse("<h3>Your are not Superuser</h3>")
