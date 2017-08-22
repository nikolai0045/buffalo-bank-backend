from rest_framework import serializers
from .models import UserProfile, CourseReport, Course, Student, Deposit, Buck, BehaviorGoal, MissingAssignment, PersonalBehaviorGoal, BehaviorNote, PurchaseItem
from tier_two.models import TTwoProfile, TTwoGoal, TTwoReport
from tier_three.models import TThreeProfile, TThreeGoal, TThreeReport
import datetime

##Bank Serializers
class StudentPersonalBehaviorGoalSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=False)

	class Meta:
		model = PersonalBehaviorGoal
		fields = ('name','description','id','active')

	def update(self,instance,validated_data):
		instance.name = validated_data.pop('name',"")
		instance.description = validated_data.pop('description',"")
		instance.active = validated_data['active']
		instance.save()
		return instance

class UserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserProfile
		fields = ('first_name','last_name','email','user_type','id','administrator','cac_administrator','pass_administrator','merchant')

class BasicUserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserProfile
		fields = ('first_name','last_name')

class BasicCourseSerializer(serializers.ModelSerializer):
	teachers = BasicUserProfileSerializer(many=True, read_only=True)

	class Meta:
		model = Course
		fields = ('name','section_number','teachers','id','hour')

class CourseReportSerializer(serializers.ModelSerializer):
	course = BasicCourseSerializer(many=False)
	start_time = serializers.TimeField(allow_null=True)
	end_time = serializers.TimeField(allow_null=True)

	class Meta:
		model = CourseReport
		fields = ('course','start_time','end_time','completed','date','id')

class BasicStudentSerializer(serializers.ModelSerializer):
	is_ttwo = serializers.BooleanField()
	is_tthree = serializers.BooleanField()
	id = serializers.IntegerField(read_only=False)
	personalbehaviorgoal_set = StudentPersonalBehaviorGoalSerializer(many=True)

	class Meta:
		model = Student
		fields = ('first_name','last_name','grade','id','account_balance','is_ttwo','is_tthree','personalbehaviorgoal_set')

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
        fields = ('student','amount_earned','buck_set','id','absent','iss')

class StudentDepositSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=False)
	buck_set = BuckSerializer(many=True)
	course_report = CourseReportSerializer()

	class Meta:
		model = Deposit
		fields = ('amount_earned','buck_set','id','course_report','absent')

class InitPersonalBehaviorGoalSerializer(serializers.ModelSerializer):
	student = BasicStudentSerializer()

	class Meta:
		model = PersonalBehaviorGoal
		fields = ('student','id','active')

	def create(self,validated_data):
		student_id = validated_data['student']['id']
		student = Student.objects.get(pk=student_id)
		new_goal = PersonalBehaviorGoal(student=student)
		new_goal.save()
		return new_goal

class CreateStudentPersonalBehaviorGoalSerializer(serializers.ModelSerializer):
	student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

	class Meta:
		model = PersonalBehaviorGoal
		fields = ('name','description','active','student','id')

class MissingAssignmentSerializer(serializers.ModelSerializer):
	course = BasicCourseSerializer()
	id = serializers.IntegerField(read_only=False)

	class Meta:
		model = MissingAssignment
		fields = ('name','description','course','date','id')

class CreateMissingAssignmentSerializer(serializers.ModelSerializer):
	course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
	students = BasicStudentSerializer(many=True)

	class Meta:
		model = MissingAssignment
		fields = ('course','students','name','description')

	def create(self,validated_data):
		new_assignment = MissingAssignment(
			name=validated_data['name'],
			description=validated_data['description'],
			course=Course.objects.get(pk=validated_data['course'].id)
		)
		new_assignment.save()
		for s in validated_data['students']:
			student = Student.objects.get(pk=s['id'])
			new_assignment.students.add(student)

		new_assignment.save()
		return new_assignment

class CourseMissingAssignmentSerializer(serializers.ModelSerializer):
	students = BasicStudentSerializer(many=True)
	course = BasicCourseSerializer()

	class Meta:
		model = MissingAssignment
		fields = ('name','description','students','date','id','course')

	def update(self,instance,validated_data):
		instance.students.clear()
		for s in validated_data['students']:
			student = Student.objects.get(pk=s['id'])
			instance.students.add(student)
		instance.name = validated_data['name']
		instance.description = validated_data['description']
		instance.save()
		return instance

##Marketplace serializers
class PurchaseItemSerializer(serializers.ModelSerializer):
	description = serializers.CharField(allow_null=True)
	id = serializers.IntegerField(read_only=True)
	quantity_remaining = serializers.IntegerField(allow_null=True)

	class Meta:
		model = PurchaseItem
		fields = ('name','current_price','quantity_remaining','description','id')

##Tier Two Serializers
class TTwoProfileSerializer(serializers.ModelSerializer):
	student = BasicStudentSerializer()
	mentor = BasicUserProfileSerializer()

	class Meta:
		model = TTwoProfile
		fields = ('student','active','mentor','id')

class TTwoGoalSerializer(serializers.ModelSerializer):
	profile = TTwoProfileSerializer()

	class Meta:
		model = TTwoGoal
		fields = ('profile','active','goal','id')

class TTwoReportSerializer(serializers.ModelSerializer):
	goal = TTwoGoalSerializer()
	report = CourseReportSerializer()
	id = serializers.IntegerField(read_only=False)

	class Meta:
		model = TTwoReport
		fields = ('goal','score','id','report','note','absent','iss')

class TTwoReportNoteSerializer(serializers.ModelSerializer):
	goal = TTwoGoalSerializer()
	report = CourseReportSerializer()

	class Meta:
		model = TTwoReport
		fields = ('goal','report','note')


##Tier Three Serializers
class TThreeGoalSerializer(serializers.ModelSerializer):

	class Meta:
		model = TThreeGoal
		fields = ('active','goal','id')

class TThreeProfileSerializer(serializers.ModelSerializer):
	student = BasicStudentSerializer()
	mentor = BasicUserProfileSerializer(allow_null=True)
	tthreegoal_set = TThreeGoalSerializer(many=True)

	class Meta:
		model = TThreeProfile
		fields = ('student','active','mentor','tthreegoal_set','id')

class TThreeReportSerializer(serializers.ModelSerializer):
	profile = TThreeProfileSerializer()
	report = CourseReportSerializer()
	id = serializers.IntegerField(read_only=False)

	class Meta:
		model = TThreeReport
		fields = ('profile','score','id','report','note','absent','iss')

class TThreeReportNoteSerializer(serializers.ModelSerializer):
	profile = TThreeProfileSerializer()
	report = CourseReportSerializer()

	class Meta:
		model = TThreeReport
		fields = ('profile','report','note')

##Student Profile Serializer

##Course Report Serializer
class FullCourseReportSerializer(serializers.ModelSerializer):
	deposit_set = FullDepositSerializer(many=True)
	course = BasicCourseSerializer()
	tthreereport_set = TThreeReportSerializer(many=True)
	ttworeport_set = TTwoReportSerializer(many=True)
	start_time = serializers.TimeField(allow_null=True)
	end_time = serializers.TimeField(allow_null=True)

	def update(self,instance,validated_data):
		for r in validated_data['ttworeport_set']:
			report = TTwoReport.objects.get(pk=r['id'])
			report.score = r['score']
			if r.has_key('note'):
				report.note = r['note']
			report.absent = r['absent']
			report.iss = r['iss']
			report.save()
		for r in validated_data['tthreereport_set']:
			report = TThreeReport.objects.get(pk=r['id'])
			report.score = r['score']
			if r.has_key('note'):
				report.note = r['note']
			report.absent = r['absent']
			report.iss = r['iss']
			report.save()
		if instance.completed == False:
			for d in validated_data['deposit_set']:
				deposit = Deposit.objects.get(pk=d['id'])
				student = deposit.student
				print d['absent']
				if d['absent']:
					deposit.absent = True
					deposit.save()
				elif d['iss']:
					deposit.iss = True
					deposit.save()
				else:
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
				if d.has_key('note'):
					deposit.note = d['note']
				deposit.save()
				if d['absent'] == True:
					deposit.absent = True
					student.account_balance -= deposit.amount_earned
					deposit.amount_earned = 0
					for b in deposit.buck_set.all():
						b.earned = False
						b.save()
					student.save()
					deposit.save()
				elif d['iss'] == True:
					deposit.iss = True
					student.account_balance -= deposit.amount_earned
					deposit.amount_earned = 0
					for b in deposit.buck_set.all():
						b.earned = False
						b.save()
					student.save()
					deposit.save()
				else:
					for b in d['buck_set']:
						buck = Buck.objects.get(pk=b['id'])
						if b['earned'] == 'true' or b['earned'] == True:
							if not buck.earned and not deposit.absent:
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
		fields = ('course','date','start_time','end_time','completed','deposit_set','tthreereport_set','ttworeport_set','id')
