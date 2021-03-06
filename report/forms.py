from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser,Reports,Review
from django import forms 

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields=('Name', 'EmpID','Attitude','TaskInterpretation','TaskUnderstanding','Approach','Communication','Execution','Commitment','Fulfillment','Performance','Comments') 

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email','primary_project','Empid','EmpName','date_join',
                  'primary_process','is_superuser', 'Designation')
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model  = CustomUser
        fields = UserChangeForm.Meta.fields
        
CHOICES = [('Present', 'Present'), ('Leave', 'leave'),('Half day leave', 'Half day leave'),('Permission', 'Permission'),
           ('WO', 'Week Off'),('OT','Over Time'),('GH','Govt Holiday'),('WFH','WFH'),('HWFH','HWFH'),('OTH','OTH')]
class ReportForm(forms.ModelForm):
    Attendence  = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(),initial='Present')
    class Meta:
        model = Reports
        fields = ('Empid','Name','Primarytask','Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments')

class ReportFormup(forms.ModelForm):
    Attendence  = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(),initial='Present')
    class Meta:
        model = Reports
        fields = ('Report_date','Attendence','Project_name', 'Subproject_name','Task','No_hours','No_count','Comments')