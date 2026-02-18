from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from users.models import User
from adminstration.models import AcademicYear, Term, SchoolClass, Section, Subject
from admission.models import AdmissionApplication, Guardian
from students.models import StudentProfile, Enrollment, TeacherAssignment
from exams.models import Exam, ExamResult
from finance.models import FeeStructure, FeePayment, Invoice, Expense, Budget
from timetable.models import Timetable, TimeSlot, TimetableEntry
from staff.models import StaffProfile, Leave, Attendance, Payroll, Department


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def overview_dashboard(request):
    """
    Comprehensive overview dashboard with metrics from all apps
    """
    now = timezone.now()
    current_year = now.year
    current_month = now.month
    
    # User Statistics
    total_users = User.objects.count()
    users_by_role = User.objects.values('role').annotate(count=Count('id'))
    active_users = User.objects.filter(is_active=True).count()
    
    # Student Statistics
    total_students = StudentProfile.objects.count()
    active_enrollments = Enrollment.objects.filter(is_active=True).count()
    students_by_class = Enrollment.objects.filter(is_active=True).values('school_class__name').annotate(count=Count('id'))
    
    # Staff Statistics
    total_staff = StaffProfile.objects.filter(is_active=True).count()
    staff_by_role = StaffProfile.objects.filter(is_active=True).values('user__role').annotate(count=Count('id'))
    
    # Admission Statistics
    total_applications = AdmissionApplication.objects.count()
    pending_admissions = AdmissionApplication.objects.filter(status='pending').count()
    accepted_admissions = AdmissionApplication.objects.filter(status='accepted').count()
    
    # Academic Statistics
    active_academic_years = AcademicYear.objects.filter(is_active=True).count()
    active_terms = Term.objects.filter(is_active=True).count()
    total_classes = SchoolClass.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.filter(is_active=True).count()
    
    # Finance Statistics
    total_fee_structures = FeeStructure.objects.filter(is_active=True).count()
    total_revenue = FeePayment.objects.filter(status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    outstanding_invoices = Invoice.objects.filter(balance__gt=0).aggregate(total=Sum('balance'))['total'] or 0
    
    # This month's finance
    month_revenue = FeePayment.objects.filter(
        status='completed',
        payment_date__month=current_month,
        payment_date__year=current_year
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    month_expenses = Expense.objects.filter(
        expense_date__month=current_month,
        expense_date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Exam Statistics
    total_exams = Exam.objects.count()
    upcoming_exams = Exam.objects.filter(date__gte=now.date()).count()
    
    # Timetable Statistics
    active_timetables = Timetable.objects.filter(is_active=True).count()
    total_time_slots = TimeSlot.objects.filter(is_active=True).count()
    
    # Staff Leave & Attendance
    pending_leaves = Leave.objects.filter(status='pending').count()
    today_attendance = Attendance.objects.filter(date=now.date()).count()
    today_present = Attendance.objects.filter(date=now.date(), status='present').count()
    
    return Response({
        'users': {
            'total': total_users,
            'active': active_users,
            'by_role': list(users_by_role)
        },
        'students': {
            'total': total_students,
            'active_enrollments': active_enrollments,
            'by_class': list(students_by_class)
        },
        'staff': {
            'total': total_staff,
            'by_role': list(staff_by_role)
        },
        'admissions': {
            'total': total_applications,
            'pending': pending_admissions,
            'accepted': accepted_admissions
        },
        'academic': {
            'active_years': active_academic_years,
            'active_terms': active_terms,
            'classes': total_classes,
            'subjects': total_subjects,
            'active_timetables': active_timetables
        },
        'finance': {
            'total_revenue': float(total_revenue),
            'total_expenses': float(total_expenses),
            'net_balance': float(total_revenue - total_expenses),
            'outstanding': float(outstanding_invoices),
            'this_month': {
                'revenue': float(month_revenue),
                'expenses': float(month_expenses),
                'net': float(month_revenue - month_expenses)
            }
        },
        'exams': {
            'total': total_exams,
            'upcoming': upcoming_exams
        },
        'hr': {
            'pending_leaves': pending_leaves,
            'today_attendance': today_attendance,
            'today_present': today_present
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """
    Dashboard focused on student-related metrics
    """
    total_students = StudentProfile.objects.count()
    active_students = StudentProfile.objects.filter(enrollments__is_active=True).distinct().count()
    
    # Enrollment by class
    enrollments_by_class = Enrollment.objects.filter(is_active=True).values(
        'school_class__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Students by gender
    students_by_gender = StudentProfile.objects.values('gender').annotate(count=Count('id'))
    
    # Recent enrollments (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_enrollments = Enrollment.objects.filter(enrolled_on__gte=thirty_days_ago).count()
    
    return Response({
        'total_students': total_students,
        'active_students': active_students,
        'by_class': list(enrollments_by_class),
        'by_gender': list(students_by_gender),
        'recent_enrollments': recent_enrollments
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_dashboard(request):
    """
    Dashboard focused on financial metrics
    """
    # Revenue breakdown
    total_revenue = FeePayment.objects.filter(status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0
    revenue_by_method = FeePayment.objects.filter(status='completed').values('payment_method').annotate(total=Sum('amount_paid'))
    
    # Expenses breakdown
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    expenses_by_category = Expense.objects.values('category').annotate(total=Sum('amount'))
    
    # Invoices
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    total_outstanding = Invoice.objects.filter(balance__gt=0).aggregate(total=Sum('balance'))['total'] or 0
    
    # Budgets
    active_budgets = Budget.objects.filter(status='active')
    total_budget = active_budgets.aggregate(total=Sum('total_budget'))['total'] or 0
    total_spent = active_budgets.aggregate(total=Sum('spent_amount'))['total'] or 0
    budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
    
    # Monthly trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month_date = timezone.now() - timedelta(days=30*i)
        month_revenue = FeePayment.objects.filter(
            status='completed',
            payment_date__month=month_date.month,
            payment_date__year=month_date.year
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        month_expenses = Expense.objects.filter(
            expense_date__month=month_date.month,
            expense_date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_trends.append({
            'month': month_date.strftime('%B %Y'),
            'revenue': float(month_revenue),
            'expenses': float(month_expenses),
            'net': float(month_revenue - month_expenses)
        })
    
    return Response({
        'revenue': {
            'total': float(total_revenue),
            'by_payment_method': [{'method': r['payment_method'], 'total': float(r['total'])} for r in revenue_by_method]
        },
        'expenses': {
            'total': float(total_expenses),
            'by_category': [{'category': e['category'], 'total': float(e['total'])} for e in expenses_by_category]
        },
        'invoices': {
            'total': total_invoices,
            'paid': paid_invoices,
            'overdue': overdue_invoices,
            'outstanding': float(total_outstanding)
        },
        'budgets': {
            'total_allocated': float(total_budget),
            'total_spent': float(total_spent),
            'utilization_percentage': round(budget_utilization, 2)
        },
        'monthly_trends': monthly_trends[::-1]  # Reverse to show oldest first
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_dashboard(request):
    """
    Dashboard focused on staff and HR metrics
    """
    # Staff overview
    total_staff = StaffProfile.objects.filter(is_active=True).count()
    staff_by_department = StaffProfile.objects.filter(is_active=True).values(
        'department__name'
    ).annotate(count=Count('id'))
    
    staff_by_employment = StaffProfile.objects.filter(is_active=True).values(
        'employment_type'
    ).annotate(count=Count('id'))
    
    # Leave statistics
    total_leaves = Leave.objects.count()
    pending_leaves = Leave.objects.filter(status='pending').count()
    approved_leaves = Leave.objects.filter(status='approved').count()
    leaves_by_type = Leave.objects.values('leave_type').annotate(count=Count('id'))
    
    # Attendance this month
    now = timezone.now()
    this_month_attendance = Attendance.objects.filter(
        date__month=now.month,
        date__year=now.year
    )
    attendance_by_status = this_month_attendance.values('status').annotate(count=Count('id'))
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(date=now.date())
    today_present = today_attendance.filter(status='present').count()
    today_absent = today_attendance.filter(status='absent').count()
    today_late = today_attendance.filter(status='late').count()
    
    # Payroll
    current_month_payroll = Payroll.objects.filter(month=now.month, year=now.year)
    payroll_processed = current_month_payroll.filter(status__in=['processed', 'paid']).count()
    total_payroll_amount = current_month_payroll.aggregate(total=Sum('net_salary'))['total'] or 0
    
    return Response({
        'staff': {
            'total': total_staff,
            'by_department': list(staff_by_department),
            'by_employment_type': list(staff_by_employment)
        },
        'leaves': {
            'total': total_leaves,
            'pending': pending_leaves,
            'approved': approved_leaves,
            'by_type': list(leaves_by_type)
        },
        'attendance': {
            'this_month': {
                'total': this_month_attendance.count(),
                'by_status': list(attendance_by_status)
            },
            'today': {
                'total': today_attendance.count(),
                'present': today_present,
                'absent': today_absent,
                'late': today_late
            }
        },
        'payroll': {
            'current_month_processed': payroll_processed,
            'current_month_total': float(total_payroll_amount)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def academic_dashboard(request):
    """
    Dashboard focused on academic metrics
    """
    # Classes and sections
    total_classes = SchoolClass.objects.filter(is_active=True).count()
    total_sections = Section.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.filter(is_active=True).count()
    
    # Students per class
    students_per_class = Enrollment.objects.filter(is_active=True).values(
        'school_class__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Teacher assignments
    total_assignments = TeacherAssignment.objects.count()
    assignments_by_subject = TeacherAssignment.objects.values(
        'subject__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    # Timetables
    active_timetables = Timetable.objects.filter(is_active=True).count()
    timetables_by_class = Timetable.objects.filter(is_active=True).values(
        'school_class__name'
    ).annotate(count=Count('id'))
    
    # Exams
    total_exams = Exam.objects.count()
    upcoming_exams = Exam.objects.filter(date__gte=now.date()).count()
    completed_exams = Exam.objects.filter(date__lt=now.date()).count()
    
    # Results
    total_results = ExamResult.objects.count()
    average_score = ExamResult.objects.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
    
    return Response({
        'structure': {
            'classes': total_classes,
            'sections': total_sections,
            'subjects': total_subjects
        },
        'enrollment': {
            'by_class': list(students_per_class)
        },
        'teachers': {
            'total_assignments': total_assignments,
            'top_subjects': list(assignments_by_subject)
        },
        'timetables': {
            'active': active_timetables,
            'by_class': list(timetables_by_class)
        },
        'exams': {
            'total': total_exams,
            'upcoming': upcoming_exams,
            'completed': completed_exams
        },
        'results': {
            'total': total_results,
            'average_score': round(average_score, 2)
        }
    })

