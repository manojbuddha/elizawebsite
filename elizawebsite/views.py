# from django.http import HttpResponse
from django.shortcuts import render
from .forms import Form1
from .elizachatbot import get_name, process_user_input, get_greetings, get_helptext

have_name = False
user_name = ""
conversations = []
latest_reply = get_greetings()

def index(request):
    global have_name
    global user_name
    global conversations
    global latest_reply
    my_dict = {'insert_me': 'Hellotest'}
    my_dict["conversations"] = conversations

    if request.method == 'POST':

        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        form1 = Form1(data=request.POST)

        # Check to see both forms are valid
        if form1.is_valid():

            print(form1.data['text'])
            user_input = form1.data['text']

            if user_input.upper() == "QUIT":
                my_dict = dict()
                have_name = False
                user_name = ""
                conversations = []
                latest_reply = get_greetings()
                form1 = Form1()
                my_dict["form1"] = form1
                my_dict["latest_reply"] = latest_reply

                return render(request, 'file1.html',
                          my_dict)
            if not have_name:
                print("get name")
                user_name = get_name(user_input)
                my_dict["user_name"] = user_name
                conversations.append((latest_reply, user_input,))
                latest_reply = get_helptext(user_name)
                have_name = True
            else:
                conversations.append((latest_reply, user_input,))
                latest_reply = process_user_input(user_input)
                print(latest_reply)

            form1 = Form1()
            my_dict["form1"] = form1
            my_dict["latest_reply"] = latest_reply
            my_dict["conversations"] = conversations[-3:]
            my_dict["user_name"] = user_name
            # print(user_name)
            return render(request, 'file1.html',
                          my_dict)
        else:
            # One of the forms was invalid if this else gets called.
            print(form1.errors)
    else:
        # Was not an HTTP post so we just render the forms as blank.
        form1 = Form1()

    my_dict["form1"] = form1
    my_dict["latest_reply"] = latest_reply
    my_dict["conversations"] = conversations
    return render(request, 'file1.html',
                  my_dict)

    # return render(request, 'file1.html', context=my_dict)
    # return HttpResponse("Hello World")
