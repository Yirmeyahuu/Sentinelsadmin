from django.shortcuts import render, redirect
from firebase_admin import firestore, initialize_app
from django.contrib import messages

# Firestore database instance
db = firestore.client()

def StudentRegister(request):
    if request.method== "POST":
        student_data = {
            "student_id": request.POST.get("student_id"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "middle_initial": request.POST.get("middle_initial"),
            "program": request.POST.get("program"),
            "year_section": request.POST.get("year_section"),
            "semester": request.POST.get("semester")
        }

        db.collection("Pending Students").document(student_data["student_id"]).set(student_data)

        # --- Add this block to create a notification ---
        full_name = f"{student_data['first_name']} {student_data['middle_initial']} {student_data['last_name']}".strip()
        notification = {
            "message": f"A student {full_name} just registered. Kindly check 'Pending Approval' menu to view student.",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "seen": False
        }
        db.collection("Notifications").add(notification)
        # ------------------------------------------------

        messages.success(request, "Student member added successfully!")
        return redirect("register_success")  # Redirect to the success page

    return render(request, 'StudentRegistration/student-registration.html')

def RegisterSuccess(request):
    return render(request, 'StudentRegistration/register-success.html')