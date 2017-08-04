from rest_framework import serializers
from .models import UserProfile, CourseReport, Course, Student, Deposit, Buck, BehaviorGoal

class UserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserProfile
		fields = ('first_name','last_name','email','user_type')

class BasicUserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserProfile
		fields = ('first_name','last_name')

class BasicCourseSerializer(serializers.ModelSerializer):
	teachers = BasicUserProfileSerializer(many=True, read_only=True)

	class Meta:
		model = Course
		fields = ('name','section_number','teachers','id')

class CourseReportSerializer(serializers.ModelSerializer):
	course = BasicCourseSerializer(many=False)

	class Meta:
		model = CourseReport
		fields = ('course','start_time','end_time','completed','date','id')

class BasicStudentSerializer(serializers.ModelSerializer):

	class Meta:
		model = Student
		fields = ('first_name','last_name','grade','id','account_balance')

class CourseStudentsSerializer(serializers.ModelSerializer):
	students = BasicStudentSerializer(many=True)

	class Meta:
		model = Course
		fields = ('name','course_number','section_number','students','id')

class BehaviorGoalSerializer(serializers.ModelSerializer):
	class Meta:
		model = BehaviorGoal
		fields = ('goal','id')
        
class BuckSerializer(serializers.ModelSerializer):
    goal = BehaviorGoalSerializer()
    id = serializers.IntegerField(read_only=False)
    class Meta:
        model = Buck
        fields = ('goal','earned','id')
        
class FullDepositSerializer(serializers.ModelSerializer):
    student = BasicStudentSerializer()
    id = serializers.IntegerField(read_only=False)
    buck_set = BuckSerializer(many=True)
    
    class Meta:
        model = Deposit
        fields = ('student','amount_earned','buck_set','id')

class FullCourseReportSerializer(serializers.ModelSerializer):
    deposit_set = FullDepositSerializer(many=True)
    course = BasicCourseSerializer()
    
    def update(self,instance,validated_data):
        if instance.completed == False:
            for d in validated_data['deposit_set']:
                deposit = Deposit.objects.get(pk=d['id'])
                student = deposit.student
                for b in d['buck_set']:
                    buck = Buck.objects.get(pk=b['id'])
                    if b['earned'] == 'true' or b['earned'] == True:
                        buck.earned = True
                        deposit.amount_earned += 1
                        student.account_balance += 1
                        student.save()
                    else:
                        buck.earned = False
                    buck.save()
                    deposit.save()
            instance.completed = True
            instance.save()
        else:
            for d in validated_data['deposit_set']:
                deposit = Deposit.objects.get(pk=d['id'])
                student = deposit.student
                for b in d['buck_set']:
                    buck = Buck.objects.get(pk=b['id'])
                    if b['earned'] == 'true' or b['earned'] == True:
                        if not buck.earned:
                            buck.earned = True
                            deposit.amount_earned += 1
                            student.account_balance += 1
                            student.save()
                            deposit.save()
                            buck.save()
                    else:
                        if buck.earned:
                            buck.earned = False
                            deposit.amount_earned -= 1
                            student.account_balance -= 1
                            student.save()
                            deposit.save()
                            buck.save()
                instance.save()
        return instance
        
    class Meta:
        model = CourseReport
        fields = ('course','date','start_time','end_time','completed','deposit_set','id')