@echo off
call C:\Users\DIVYANSHU TANDON\Desktop\VT_Project\env\Scripts\activate
pip install -r requirements.txt
python manage.py collectstatic --noinput