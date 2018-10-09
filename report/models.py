from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUserManager(UserManager):
    pass
class CustomUser(AbstractUser):
    objects         = CustomUserManager()
    id              = models.AutoField(primary_key=True)
    primary_project = models.CharField(max_length=250)
    Empid           = models.IntegerField()
    EmpName         = models.CharField(max_length=250)
    date_join       = models.DateField(blank=True, null=True)   
    primary_process = models.CharField(max_length=250)
    processwillInclude = models.CharField(blank=True, max_length=250)
    Designation = models.CharField(blank=True, max_length=250, null=True)
    def __str__(self):
        return self.EmpName
    def split_tags(self):
        return self.processwillInclude.split(',')

class Project(models.Model):
    Projectname = models.CharField(max_length=30)
    def __str__(self):
        return self.Projectname

class Subproject(models.Model):
    Project_name    = models.ForeignKey(Project, on_delete=models.CASCADE)
    Subproject_name = models.CharField(max_length=30)

    def __str__(self):
        return self.Subproject_name

class Reports(models.Model):
    TASK_TYPES = (
        ('Scripting', 'Scripting'),
        ('Re-scripting', 'Rescripting'),
        ('Analysis', 'Analysis'),
        ('Manual', 'Manual'),
    )
    id    = models.AutoField(primary_key=True,null=False)
    Empid = models.IntegerField(default='', blank=True)
    Name  = models.CharField(max_length=50, blank=True)
    Primarytask      = models.CharField(max_length=50,default='', blank=True)
    Report_date      = models.DateField(null=True,blank=False)
    Attendence      =  models.CharField(max_length=50,default='')
    Project_name    = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True,blank=True)
    Subproject_name = models.ForeignKey(Subproject, on_delete=models.SET_NULL, null=True,blank=True)
#     Task       = models.CharField(max_length=20, default="")
    Task       = models.CharField(choices=TASK_TYPES,max_length=50,blank=True)
    No_hours   = models.DecimalField((u"Number of Hours"),max_digits=9, decimal_places=2,blank=True,default=0)
    No_count   = models.IntegerField(default=0,blank=True)
    Comments   = models.CharField(max_length=500,default='',blank=False)
    dtcollected = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.Name
    
class datesofmonth(models.Model):
    id = models.AutoField(primary_key=True)
    weekday = models.DateField()