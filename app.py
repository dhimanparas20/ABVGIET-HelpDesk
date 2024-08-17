from flask import Flask, redirect, render_template,make_response,send_file ,send_from_directory,url_for
from flask_restful import Resource, Api ,request 
from os import system, getcwd,path,getenv
import pyqrcode
import png

system("clear")
cwd = getcwd()

# The function that predicts lectures.
def check(curr_lec,tot_lec):
  temp = curr_lec
  per=(curr_lec/tot_lec)*100
  perc =per
  if per >=75:
    print("\n--------| PERCENTAGE IN SAFE ZONE |--------\n")
    no = curr_lec-temp
    no,curr_lec,tot_lec = 0,0,0
    return no,curr_lec,tot_lec,perc
  else:
    while per < 75 :
      curr_lec +=1
      tot_lec +=1
      per =  (curr_lec/tot_lec)*100
    return curr_lec-temp,curr_lec,tot_lec,perc

# converts any base to decimal base     
def conv_decimal(num,base):
  ln = len(str(num))
  i,dec = 0,0
  while ln > 0:
    rem = num%10
    num = int(num/10) 
    dec = dec + rem*(base**i)
    ln -= 1
    i += 1     
  return dec

# converts decimal number to any base  
def conv_n(num,base):
    base_num = ""
    while num>0:
        dig = int(num%base)
        if dig<10:
            base_num += str(dig)
        else:
            base_num += chr(ord('A')+dig-10)  #Using uppercase letters
        num //= base

    base_num = base_num[::-1]  #To reverse the string
    return base_num

# converts from any base to any base
def convert(num,frm,to):
  if to == 10:
      return conv_decimal(num,frm)
  else:
    print("")
    return (conv_n(conv_decimal(num,frm),to))

#Returns f (from)
def ret_from(frm):
  if frm  == "binary":
    f = 2
  elif frm  ==  "octal":
    f = 8
  elif frm  ==  "decimal":
    f = 10
  elif frm  ==  "hexa":
    f = 16 
  else:
    f = 10
  return f  

def ret_to(to):
  if to  == "binary":
    t = 2
  elif to  ==  "octal":
    t = 8
  elif to  ==  "decimal":
    t = 10
  elif to  ==  "hexa":
    t = 16  
  else:
    t = 10  
  return t  

#Giving API a Name
app = Flask(__name__)
api = Api(app)

#Redirect to Home page
class Base(Resource):
    def get(self):
        search = request.args.get("search")
        return redirect(url_for('home')) 

#Home page      
class Home(Resource):
    def get(self):
      return make_response(render_template("home.html"))

# Syllabus    
class Syllabus(Resource):
    def get(self):
        return make_response(render_template("syllabus.html"))    

# Returns Syllabus
class Download_Syllabus(Resource):
    def get(self):
        print("---------|DOWNLOADING Syllabus|--------------")
        return send_from_directory(f"{cwd}/content/syllabus","combined_cbcs.pdf",as_attachment=True)    

# Lecture Predict    
class Lecture_Predict(Resource):
    def get(self): 
      curr_lec = request.args.get('curr_lec')
      tot_lec = request.args.get('tot_lec')
      name = request.args.get('name')
      print(name,curr_lec,tot_lec)   
      #For default page
      if curr_lec  == None or name == None:
        curr_lec,tot_lec,name = 1,1,""
      tmp,v1,v2,perc = check(int(curr_lec),int(tot_lec))
      return make_response(render_template('lecture_predict.html',temp=tmp,val1=v1,val2=v2,per=perc,name=name,curr_lec=curr_lec,tot_lec=tot_lec))  

# Base Conversion    
class Convert(Resource):
    def get(self):
      frm = request.args.get('frm')
      to = request.args.get('to')
      v1 = request.args.get('value1')
      f = ret_from(frm)
      t = ret_to(to)     
      # Set v1 initially when site loads  
      if v1 == None:
        v1 = "0"
        
      output = convert(int(v1),f,t)
      if output == 0:
        output,v1,f,t= None,None,0,0 
      return make_response(render_template('convert.html',output=output,v1=v1,base1=f,base2=t,frm=frm,to=to))          

#Download Books
class Download(Resource):
    def get(self):  
      return make_response(render_template('download.html',location=cwd))

#Returns pdf from database 
class Content(Resource):
    def get(self,filename,dir):
      print(dir,filename)
      return send_from_directory(f"{cwd}/content/{dir}",filename,as_attachment=True)  
 

#Return Bus Timing page      
class Bus_Timing(Resource):
    def get(self):
      return make_response(render_template('bus_timing.html')) 

#Returns Contacts Page    
class Contacts(Resource):
    def get(self):
      return make_response(render_template('contacts.html'))  
  
#Generate QR-Code
class Qr(Resource):
    def get(self):
      name = request.args.get("name")
      size = request.args.get("size")
      if name == None and size == None:
        print("delete complete")
        system(f"rm -rf {cwd}/static/qr.png")
        return make_response(render_template('qr.html'))             
      url = pyqrcode.create(name)
      url.png(f"{cwd}/static/qr.png",scale = size)
      print("---------|DOWNLOADING QR|--------------")
      return send_from_directory(f"{cwd}/static/","qr.png",as_attachment=True)
#Routes    
api.add_resource(Base, '/', methods=['GET', 'POST'])
api.add_resource(Home, '/home/', methods=['GET', 'POST'])
api.add_resource(Syllabus, '/syllabus/', methods=['GET', 'POST'])
api.add_resource(Download_Syllabus, '/download_syllabus/', methods=['GET', 'POST'])
api.add_resource(Download, '/download/', methods=['GET', 'POST'])
api.add_resource(Content, '/content/<dir>/<filename>/', methods=['GET', 'POST'])
api.add_resource(Lecture_Predict, '/lecture_predict/', methods=['GET', 'POST'])
api.add_resource(Convert, '/convert/', methods=['GET', 'POST'])  
api.add_resource(Bus_Timing, '/bus_timing/', methods=['GET', 'POST'])
api.add_resource(Contacts, '/contacts/', methods=['GET', 'POST'])
api.add_resource(Qr, '/qr/', methods=['GET', 'POST'])

#Running the Web-App Debug Mode
if __name__ == '__main__':
    app.run(debug=True,port=5000,host="0.0.0.0",threaded=True)
