# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Template, Context
from django.shortcuts import render, render_to_response
from django.views.generic import TemplateView
from django.http import HttpResponse

from controller_app.models import Controllers, Usuarios
import numpy
import matplotlib.pyplot as plt
import datetime
import requests

# Create your views here.


class controller_class(TemplateView):

  
    def get(self, request, **kwargs):

        return render(request, 'controller_app/controller_login.html') 

   
    def post(self, request, *args, **kwargs):

#######################carga pagina inicial #########################

        if (request.POST.get("uname", "")):
           uname=request.POST.get("uname", "")
           psw=request.POST.get("psw", "")
  
           usuarios_sql= Usuarios.objects.all()
           n_usuarios=numpy.size(usuarios_sql) 
           o_t=[]
   
           user="no"
           for i_usuarios in range(0,n_usuarios,1):
              usuario=Usuarios.objects.get(id=i_usuarios+1)

              if usuario.usuarios_correo==uname and usuario.password==psw:
                 user="yes"
                 controllers_sql=Controllers.objects.filter(usuarios=uname)
                 n_controllers=numpy.size(controllers_sql)

              
              
                 for i_campos in range(0,n_controllers,1):
                     controller_temp=controllers_sql[i_campos]
                     pushbutton_pos=50+i_campos*80
                     number_pos=str(i_campos).zfill(2)
                     coord=  controller_temp.lat_lng 
                     id_number=controller_temp.id
                     name=controller_temp.controller
                  
                     o_t.append((id_number,coord,name,str(pushbutton_pos)))  

                 coord_center=controllers_sql[0].controller_coordinates
                 coord_center=coord_center.split() 
                 return render(request, 'controller_app/controller_main_01.html',{'data': o_t,'coordx':coord_center[0],'coordy':coord_center[1]}) 

          
           if user=="no":            
              return render(request, 'controller_app/controller_login.html') 

################################listas del controlador####################################
        
        valve_states=['off','on']
        valve_fig_VP=["VP_OFF_v2.png","VP_ON_v2.png"]
        valve_fig_R=["OFF","ON"] 

        valve_name=["PRINCIPAL","SECTOR 01","SECTOR 02","SECTOR 03","SECTOR 04","SECTOR 05","SECTOR 06"]
        button_pos=["TOP:70px; LEFT:250px;","TOP:30px; LEFT:450px;","TOP:120px; LEFT:450px;","TOP:30px; LEFT:650px;","TOP:120px; LEFT:650px;","TOP:30; LEFT:850px;","TOP:120px; LEFT:850px;"]
        valve_pos=["TOP:277px; LEFT:923px; WIDTH:94px; HEIGHT:110px", "TOP:40px; LEFT:1179px; WIDTH:72px; HEIGHT:80px", "TOP:120px; LEFT:1179px; WIDTH:72px; HEIGHT:80px", "TOP:202px; LEFT:1179px; WIDTH:72px; HEIGHT:80px","TOP:400px; LEFT:1179px; WIDTH:72px; HEIGHT:80px","TOP:480px; LEFT:1179px; WIDTH:72px; HEIGHT:80px","TOP:560px; LEFT:1179px; WIDTH:72px; HEIGHT:80px"]   


#######################carga pagina  del controlador#########################
          
        if (request.POST.get("title", "")):  
           controller_id=request.POST.get("title", "")
           a= 'none'
           controller=Controllers.objects.get(id=int(controller_id))
           n_sectores=controller.numero_sectores
           url=controller.web_direction 
           write_control_calendario=controller.control_calendario_put 
           read_control_calendario=controller.read_control_calendario
           serial_number=controller.serial_number

        #############################checkea conexion#################################### 
           now = datetime.datetime.now()
           MyString = now.strftime("%Y-%m-%d %H:%M:%S")
           MyString=MyString.split()
           MyString=MyString[1].split(':')
           Min=int(MyString[0])*60+int(MyString[1])

           hora_cont=self.lectura_datos_controller(controller_id)[6]
           hora_cont=hora_cont[-1]
           hora_cont=hora_cont.split(':')
           Min_C=int(hora_cont[0])*60+int(hora_cont[1])
           conexion_OK='0'
           if abs(Min_C-Min)<6:
              conexion_OK='1'

        #############################checkea estado valvulas#################################### 
           control_calendario = requests.put(url+read_control_calendario, data = serial_number)
         
           content=control_calendario.content
       
           index=0
           while content[index:index+6]!='datos_':
               index=index+1
       
           index2=index
           while content[index2:index2+4]!='_fin':
               index2=index2+1
           
           content=content[index+6:index2]  
           content=list(content)

           VP_status=valve_states[int(content[0])-1] 
           list_template=[(valve_states[int(content[1])-1], 1, valve_pos[0], button_pos[0],valve_name[0],valve_fig_R[int(content[1])-1])]
         
           for i_valve in range(0,int(n_sectores),1):
              list_template.append((valve_states[int(content[i_valve+2])-1], int(i_valve+2), valve_pos[i_valve+1], button_pos[i_valve+1], valve_name[i_valve+1],valve_fig_R[int(content[i_valve+2])-1])) 

 
           template='controller_app/controller_second_extends_tub_%s.html' % n_sectores

           return render(request, template,{'data':list_template,'id':controller_id,'popup':a,'graphics':a,'VP':VP_status,'conexion':conexion_OK})


#######################push button ON/OFF#########################
          
        if (request.POST.get("controller_button", "")):  

           push_button=request.POST.get("controller_button", "")
           push_button=push_button.split(':') 
           controller_id=push_button[0]
           a= 'none'  
           MA='0'  
           try:
              valve_change=int(push_button[1]) 
           except:
              MA='1'
  
           fid=open('controller_idpb2','w')
           fid.write(MA)
           fid.close()

           controller=Controllers.objects.get(id=int(controller_id))
           n_sectores=controller.numero_sectores
           url=controller.web_direction 
           write_control_calendario=controller.control_calendario_put 
           read_control_calendario=controller.read_control_calendario
           serial_number=controller.serial_number
           fid=open('controller_idpb','w')
           fid.write(serial_number)
           fid.close() 
        #############################checkea estado valvulas#################################### 
           control_calendario = requests.put(url+read_control_calendario, data = serial_number)
           
           content=control_calendario.content
           
      
           index=0
           while content[index:index+6]!='datos_':
               index=index+1
       
           index2=index
           while content[index2:index2+4]!='_fin':
               index2=index2+1
          
           content=content[index+6:index2]  
           fid=open('controller_idpb2','w')
           fid.write(content[0:12])
           fid.close() 
           content=list(content)
      
           if MA=='0':  
             if content[valve_change]=='1':
                content[valve_change]='2'
             else:
                content[valve_change]='1'
           
           if MA=='1':
             if content[0]=='1':
                content[0]='2'
             else:
                content[0]='1'    

           content="".join(content)
           fid=open('controller_idpb3','w')
           fid.write(content[0:12])
           fid.close()
           data_put=serial_number+content       
           put_control = requests.put(url+write_control_calendario, data = data_put) 

        ################################genera lista para el template####################################
     

           VP_status=valve_states[int(content[0])-1]
           list_template=[(valve_states[int(content[1])-1], 1, valve_pos[0], button_pos[0],valve_name[0],valve_fig_R[int(content[1])-1])]
         
           for i_valve in range(0,int(n_sectores),1):
              list_template.append((valve_states[int(content[i_valve+2])-1], int(i_valve+2), valve_pos[i_valve+1], button_pos[i_valve+1], valve_name[i_valve+1],valve_fig_R[int(content[i_valve+2])-1]))


 
           template='controller_app/controller_second_extends_tub_%s.html' % n_sectores
           
           return render(request, template,{'data':list_template,'id':controller_id,'popup':a,'graphics':a,'VP':VP_status})

#######################popup calendario#########################

        if (request.POST.get("popup", "")): 

           temp=request.POST.get("popup", "")
           temp=temp.split(':')
           controller_id=temp[0]
           content=self.get_controller(controller_id)[0]
           MIF_all=self.get_controller(controller_id)[1]
           checkbox_state=self.get_controller(controller_id)[2]
          # fid=open('controller_idpb2','w')
          # fid.write(MIF_all)
          # fid.close()

           controller=Controllers.objects.get(id=int(controller_id))
           n_sectores=controller.numero_sectores

           VP_status=valve_states[int(content[0])-1]
           list_template=[(valve_states[int(content[1])-1], 1, valve_pos[0], button_pos[0],valve_name[0],valve_fig_R[int(content[1])-1])]
         
           for i_valve in range(0,int(n_sectores),1):
              list_template.append((valve_states[int(content[i_valve+2])-1], int(i_valve+2), valve_pos[i_valve+1], button_pos[i_valve+1], valve_name[i_valve+1],valve_fig_R[int(content[i_valve+2])-1]))


           popup='popup'
           graphics='none'

           checkbox_pos=['TOP:250px; LEFT:60px;','TOP:250px; LEFT:100px;','TOP:250px; LEFT:140px;','TOP:250px; LEFT:180px;','TOP:250px; LEFT:220px;','TOP:250px; LEFT:260px;','TOP:250px; LEFT:300px;']
           pos_input=['TOP:80px; LEFT:120px;', 'TOP:130px; LEFT:120px;','TOP:80px; LEFT:220px;','TOP:130px; LEFT:220px;','TOP:80px; LEFT:320px;','TOP:130px; LEFT:320px;','TOP:80px; LEFT:420px;','TOP:130px; LEFT:420px;','TOP:80px; LEFT:520px;','TOP:130px; LEFT:520px;','TOP:80px; LEFT:620px;','TOP:130px; LEFT:620px;']
           pos_name=['TOP:20px; LEFT:120px;', 'TOP:20px; LEFT:220px;', 'TOP:20px; LEFT:320px;', 'TOP:20px; LEFT:420px;', 'TOP:20px; LEFT:520px;', 'TOP:20px; LEFT:620px;']
           name_sector=['sector 01','sector 02','sector 03','sector 04','sector 05','sector 06']
           template='controller_app/controller_second_extends_tub_%s.html' % n_sectores

           input_sectores=[] 
           for i_sector in range(0, int(n_sectores),1):
              input_sectores.append((pos_input[i_sector*2],pos_input[i_sector*2+1],pos_name[i_sector],name_sector[i_sector],str(i_sector+2),MIF_all[i_sector*2],MIF_all[i_sector*2+1]))

           checkbox_data=[]               
           for i_dia in range(0,7,1):
               checkbox_data.append((str(int(checkbox_state[i_dia])),checkbox_pos[i_dia],str(i_dia)))

           return render(request, template,{'data':list_template,'id':controller_id,'popup':popup,'graphics':graphics,'VP':VP_status,'position_input_popup':input_sectores,'checkbox':checkbox_data})


#######################recibir calendario#########################

        if (request.POST.get("cargar_datos", "")): 

           controller_id=request.POST.get("cargar_datos", "")
           controller=Controllers.objects.get(id=int(controller_id))
           n_sectores=controller.numero_sectores   
           url=controller.web_direction 
           write_control_calendario=controller.control_calendario_put 
           read_control_calendario=controller.read_control_calendario
           serial_number=controller.serial_number

           content=self.get_controller(controller_id)[0]
           MIF_all=self.get_controller(controller_id)[1]
           checkbox_state=self.get_controller(controller_id)[2]
           num_ini=self.get_controller(controller_id)[3]
            
           H_ini=[]  
           H_D=[]
           checkbox_status=[]

           for i_dia in range(0,7,1):
               temp=request.POST.get("checkbox%s" % str(i_dia), "") 
               checkbox_status.append(temp) 

           for i_sector in range(2,int(n_sectores)+2,1):
               temp=request.POST.get("date_ini:%s" % i_sector, "") 
               temp=temp.split(':')
               H_ini.append(int(temp[0])*60+int(temp[1]))

               temp=request.POST.get("date_fin:%s" % i_sector, "") 
               temp=temp.split(':')
               H_D.append(int(temp[0])*60+int(temp[1])) 
           

           #genera content inicial
           DMI=[]
           DMF=[]

           for i_dia in range(0,7,1):
               if checkbox_status[i_dia]=='on':
                  for i_sector in range(0,int(n_sectores),1):
                      DMI.append(str(H_ini[i_sector]).zfill(4))
                      DMF.append(str(H_D[i_sector]+H_ini[i_sector]).zfill(4))
                  for i_sector in range(int(n_sectores),6,1):
                      DMI.append('0000')
                      DMF.append('0000')
               else:
                  for i_sector in range(0,6,1):
                      DMI.append('0000')
                      DMF.append('0000')
                      
####################################################################
            # define string calendario
#####################################################################            
   
           if num_ini<8:
              num_ini=num_ini+1
           if num_ini==9:
              nun_ini=3
            
           rad=1

           string_calendario=str(num_ini)+'1111111&'
           for i_dia in range(0,7,1):
               string_calendario=string_calendario+str(i_dia+1)+'&'
               for i_sector in range(0,6,1):
                   string_calendario=string_calendario+DMI[i_dia*6+i_sector]+'&'+DMF[i_dia*6+i_sector]+'&'
  
           string_calendario=string_calendario+str(rad)+'&'

           #cambia en el servidor estado de valvulas
           data_put=serial_number+string_calendario
           put_control = requests.put(url+write_control_calendario, data = data_put)
           try: 
              status=put_control.status_code
              reason=put_control.reason
              content2=put_control.content
              if status != 200 and status != 201:
                    try:
                        if (reason != None):
                            print('HTTP Failure Reason: ' + reason + ' body: ' + content)
                        else:
                            print('HTTP Failure Body: ' + content)
                    except Exception:
                        print('HTTP Failure Status: %d' % (status) )


           except Exception as e:
                print('HTTP Failure: ' + str(e))
           
           finally:
                if put_control != None:
                    put_control.close      

           fid=open('controller_temp1','w')
           fid.write(string_calendario)
           fid.close()

           
           #crea template

           VP_status=valve_states[int(content[0])-1]
           list_template=[(valve_states[int(content[1])-1], 1, valve_pos[0], button_pos[0],valve_name[0],valve_fig_R[int(content[1])-1])]
         
           for i_valve in range(0,int(n_sectores),1):
              list_template.append((valve_states[int(content[i_valve+2])-1], int(i_valve+2), valve_pos[i_valve+1], button_pos[i_valve+1], valve_name[i_valve+1],valve_fig_R[int(content[i_valve+2])-1]))


           popup='popup_ok'
           graphics='none'

           checkbox_pos=['TOP:250px; LEFT:60px;','TOP:250px; LEFT:100px;','TOP:250px; LEFT:140px;','TOP:250px; LEFT:180px;','TOP:250px; LEFT:220px;','TOP:250px; LEFT:260px;','TOP:250px; LEFT:300px;']
           pos_input=['TOP:80px; LEFT:120px;', 'TOP:130px; LEFT:120px;','TOP:80px; LEFT:220px;','TOP:130px; LEFT:220px;','TOP:80px; LEFT:320px;','TOP:130px; LEFT:320px;','TOP:80px; LEFT:420px;','TOP:130px; LEFT:420px;','TOP:80px; LEFT:520px;','TOP:130px; LEFT:520px;','TOP:80px; LEFT:620px;','TOP:130px; LEFT:620px;']
           pos_name=['TOP:20px; LEFT:120px;', 'TOP:20px; LEFT:220px;', 'TOP:20px; LEFT:320px;', 'TOP:20px; LEFT:420px;', 'TOP:20px; LEFT:520px;', 'TOP:20px; LEFT:620px;']
           name_sector=['sector 01','sector 02','sector 03','sector 04','sector 05','sector 06']
           template='controller_app/controller_second_extends_tub_%s.html' % n_sectores

           input_sectores=[] 
           for i_sector in range(0, int(n_sectores),1):
              input_sectores.append((pos_input[i_sector*2],pos_input[i_sector*2+1],pos_name[i_sector],name_sector[i_sector],str(i_sector+2),MIF_all[i_sector*2],MIF_all[i_sector*2+1]))

           checkbox_data=[]               
           for i_dia in range(0,7,1):
               checkbox_data.append((str(int(checkbox_state[i_dia])),checkbox_pos[i_dia],i_dia))

           return render(request, template,{'data':list_template,'id':controller_id,'popup':popup,'graphics':graphics,'VP':VP_status,'position_input_popup':input_sectores,'checkbox':checkbox_data})


#######################graphics#########################

        if (request.POST.get("graphics", "")): 

           temp=request.POST.get("graphics", "")
           temp=temp.split(':')
           controller_id=temp[0]
           a0=self.lectura_datos_controller(controller_id)[0]
           a1=self.lectura_datos_controller(controller_id)[1]
           a2=self.lectura_datos_controller(controller_id)[2]
           a3=self.lectura_datos_controller(controller_id)[3]
           a4=self.lectura_datos_controller(controller_id)[4]
           

           plt.plot(a0,'k')
           plt.savefig('controller_app/static/controller_app/a0.png')
           plt.plot(a1,'k')
           plt.savefig('controller_app/static/controller_app/a1.png')
           plt.plot(a2,'k')
           plt.savefig('controller_app/static/controller_app/a2.png')
           plt.plot(a3,'k')
           plt.savefig('controller_app/static/controller_app/a3.png')
           plt.plot(a4,'k')
           plt.savefig('controller_app/static/controller_app/a4.png')

           template='controller_app/controller_graphs.html'
           return render(request, template, {'id':controller_id})


    def lectura_datos_controller(self,controller_id):
         
        controller=Controllers.objects.get(id=int(controller_id))
        n_sectores=controller.numero_sectores
        url=controller.web_direction 
        write_control_calendario=controller.control_calendario_put 
        read_control_calendario=controller.read_control_calendario
        serial_number=controller.serial_number
        read_analog=controller.read_analog_reading

       
        analog_data = requests.put(url+read_analog, data = serial_number)  
        content=analog_data.content
        print(serial_number)
        index=0
        while content[index:index+6]!='datos_':
            index=index+1
       
        index2=index
        while content[index2:index2+4]!='_fin':
            index2=index2+1
           
        content=content[index+6:index2]  
        print(content)
        index=0       
        index_c=[0]

        while index<len(content):
         
          if content[index:index+2]=='&&':
              index_c.append(index)
           
          index=index+1
          
        a0=[]
        a1=[]
        a2=[]
        a3=[]
        a4=[]
        a5=[] 
        dia=[]
        mes=[]
        hora=[]
        for i_c in range(0,len(index_c)-1,1):
            
            if content[index_c[i_c]+5]==',':
               try:
                  a0_temp=float(content[index_c[2]+35:index_c[2]+38])/1023*5
                  a1_temp=float(content[index_c[2]+39:index_c[2]+42])/1023*5
                  a2_temp=float(content[index_c[2]+43:index_c[2]+46])/1023*5
                  a3_temp=float(content[index_c[2]+47:index_c[2]+50])/1023*5
                  a4_temp=float(content[index_c[2]+51:index_c[2]+54])/1023*5
                  a5_temp=float(content[index_c[2]+55:index_c[2]+58])/1023*5
                  a0.append(a0_temp)                  
                  a1.append(a0_temp)
                  a2.append(a0_temp)
                  a3.append(a0_temp)
                  a4.append(a0_temp)
                  a5.append(a0_temp)   
                  mes.append(content[index_c[2]+10:index_c[2]+13])
                  dia.append(content[index_c[2]+7:index_c[2]+9]) 
                  hora.append(content[index_c[2]+19:index_c[2]+27])  
               except:
                  pass 

        return a0, a1, a2, a3, a4, a5, hora, dia, mes    




    def get_controller(self,controller_id):
         
        controller=Controllers.objects.get(id=int(controller_id))
        n_sectores=controller.numero_sectores
        url=controller.web_direction 
        write_control_calendario=controller.control_calendario_put 
        read_control_calendario=controller.read_control_calendario
        serial_number=controller.serial_number

        #############################checkea estado valvulas#################################### 
        control_calendario = requests.put(url+read_control_calendario, data = serial_number)
          
        content=control_calendario.content
  
        index=0
        while content[index:index+6]!='datos_':
            index=index+1
       
        index2=index
        while content[index2:index2+4]!='_fin':
            index2=index2+1
          
        content=content[index+6:index2] 
 
        data_cal=content
        num_ini=int(data_cal[0])  
        #obtiene horarios del fichero
        MIF=[]
        for ii in range(0,7,1):
           for jj in range(0,12,1):
               MIF.append(data_cal[11+62*ii+5*jj:11+62*ii+5*(jj+1)-1])

               
        rad=data_cal[11+62*ii+5*(jj+1)]

        if rad=='1':
      
             #carga los valores 
             checkbox_state=numpy.zeros(7)
             dia_OK=-1
             for i_dia in range(0,7,1):

                 MIF_t=0
                 for i_sector in range(0,int(n_sectores)*2,1):
                     MIF_t=MIF_t+int(MIF[i_dia*12+i_sector])
                     
                 if MIF_t==0:   
                     checkbox_state[i_dia]=1   
                 else:
                     dia_OK=i_dia                 

             MIF_all=numpy.zeros((12))
             
             if dia_OK!=-1:

                 for i_sector in range(0,12,1):
                    MIF_all[i_sector]=MIF[dia_OK*12+i_sector]

             MIF_time_all=[]             
             for i_sector in range(0,int(n_sectores),1):
                   M_inicial=MIF_all[i_sector*2]
                   M_final=MIF_all[i_sector*2+1]
                   M_final=M_final-M_inicial 
                   
                   hour=int(int(M_inicial)/60)
                   minuto=int(int(M_inicial)-hour*60)  
                   MIF_time_all.append('%s:%s' % (str(hour).zfill(2), str(minuto).zfill(2)))             
                   
                   hour=int(int(M_final)/60)
                   minuto=int(int(M_final)-hour*60)  
                   MIF_time_all.append('%s:%s' % (str(hour).zfill(2), str(minuto).zfill(2))) 

             for i_sector in range(0,int(n_sectores),1):
                   M_inicial=MIF[i_sector*2]
                   M_final=MIF[i_sector*2+1]
                   
                   hour=int(int(M_inicial)/60)
                   minuto=int(int(M_inicial)-hour*60)
  
                   hour=int(int(M_final)/60)
                   minuto=int(int(M_final)-hour*60)




       
        return content, MIF_time_all, checkbox_state, num_ini 
