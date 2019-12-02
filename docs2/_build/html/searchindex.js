Search.setIndex({docnames:["admin/activities","admin/attendance","admin/calendar","admin/events","admin/index","admin/jobs","admin/locations","admin/overview","admin/roles","dev/index","dev/shotglass2","dev/staffing","index"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["admin/activities.rst","admin/attendance.rst","admin/calendar.rst","admin/events.rst","admin/index.rst","admin/jobs.rst","admin/locations.rst","admin/overview.rst","admin/roles.rst","dev/index.rst","dev/shotglass2.rst","dev/staffing.rst","index.rst"],objects:{"":{app:[11,0,0,"-"]},"shotglass2.shotglass":{"static":[10,1,1,""],get_app_config:[10,1,1,""],get_site_config:[10,1,1,""],initalize_user_tables:[10,1,1,""],make_db_path:[10,1,1,""],register_www:[10,1,1,""],set_template_dirs:[10,1,1,""]},"shotglass2.takeabeltof":{database:[10,0,0,"-"],date_utils:[10,0,0,"-"],jinja_filters:[10,0,0,"-"],mailer:[10,0,0,"-"]},"shotglass2.takeabeltof.database":{Database:[10,2,1,""],SqliteTable:[10,2,1,""]},"shotglass2.takeabeltof.database.Database":{connect:[10,3,1,""],cursor:[10,3,1,""]},"shotglass2.takeabeltof.database.SqliteTable":{"delete":[10,3,1,""],"new":[10,3,1,""],commit:[10,3,1,""],create_table:[10,3,1,""],get:[10,3,1,""],get_column_names:[10,3,1,""],init_table:[10,3,1,""],query:[10,3,1,""],query_one:[10,3,1,""],rows_to_namedlist:[10,3,1,""],save:[10,3,1,""],select:[10,3,1,""],select_one:[10,3,1,""],select_one_raw:[10,3,1,""],select_raw:[10,3,1,""],set_defaults:[10,3,1,""],update:[10,3,1,""]},"shotglass2.takeabeltof.date_utils":{date_to_string:[10,1,1,""],datetime_as_string:[10,1,1,""],getDatetimeFromString:[10,1,1,""],get_time_zone_setting:[10,1,1,""],local_datetime_now:[10,1,1,""],make_tz_aware:[10,1,1,""],nowString:[10,1,1,""]},"shotglass2.takeabeltof.jinja_filters":{abbr_date_string:[10,1,1,""],iso_date_string:[10,1,1,""],local_date_and_time_string:[10,1,1,""],local_date_string:[10,1,1,""],local_time_string:[10,1,1,""],long_date_string:[10,1,1,""],render_markdown:[10,1,1,""],short_abbr_date_string:[10,1,1,""],short_date_string:[10,1,1,""],short_day_and_date_and_time_string:[10,1,1,""],short_day_and_date_string:[10,1,1,""],weblink:[10,1,1,""]},"shotglass2.takeabeltof.mailer":{email_admin:[10,1,1,""],send_message:[10,1,1,""]},"shotglass2.users":{admin:[10,0,0,"-"],models:[10,0,0,"-"]},"shotglass2.users.admin":{Admin:[10,2,1,""]},"shotglass2.users.admin.Admin":{has_access:[10,3,1,""],has_user_table_access:[10,3,1,""],register:[10,3,1,""]},"shotglass2.users.models":{Pref:[10,2,1,""],Role:[10,2,1,""],User:[10,2,1,""],UserRole:[10,2,1,""],init_db:[10,1,1,""]},"shotglass2.users.models.Pref":{create_table:[10,3,1,""],get:[10,3,1,""]},"shotglass2.users.models.Role":{create_table:[10,3,1,""],get:[10,3,1,""],init_table:[10,3,1,""]},"shotglass2.users.models.User":{"delete":[10,3,1,""],add_role:[10,3,1,""],clear_roles:[10,3,1,""],create_table:[10,3,1,""],get:[10,3,1,""],get_by_username_or_email:[10,3,1,""],get_roles:[10,3,1,""],get_with_roles:[10,3,1,""],init_table:[10,3,1,""],is_admin:[10,3,1,""],max_role_rank:[10,3,1,""],select:[10,3,1,""],update_last_access:[10,3,1,""],user_has_role:[10,3,1,""]},"shotglass2.users.models.UserRole":{create_table:[10,3,1,""]},"shotglass2.users.views":{login:[10,0,0,"-"],password:[10,0,0,"-"],pref:[10,0,0,"-"],user:[10,0,0,"-"]},"shotglass2.users.views.login":{authenticate_user:[10,1,1,""],quite_test_fixture:[10,1,1,""],recover_password:[10,1,1,""]},"shotglass2.users.views.password":{getPasswordHash:[10,1,1,""],matchPasswordToHash:[10,1,1,""]},"shotglass2.users.views.pref":{get_contact_email:[10,1,1,""]},"shotglass2.users.views.user":{activate:[10,1,1,""],admin:[10,1,1,""],register:[10,1,1,""],save_table_search:[10,1,1,""]},"staffing.models":{Activity:[11,2,1,""],ActivityType:[11,2,1,""],Attendance:[11,2,1,""],Client:[11,2,1,""],Event:[11,2,1,""],EventDateLabel:[11,2,1,""],Job:[11,2,1,""],JobRole:[11,2,1,""],Location:[11,2,1,""],StaffNotification:[11,2,1,""],Task:[11,2,1,""],UserJob:[11,2,1,""],init_event_db:[11,1,1,""]},"staffing.models.Activity":{create_table:[11,3,1,""]},"staffing.models.ActivityType":{create_table:[11,3,1,""]},"staffing.models.Attendance":{create_table:[11,3,1,""]},"staffing.models.Client":{create_table:[11,3,1,""]},"staffing.models.Event":{create_table:[11,3,1,""],select:[11,3,1,""]},"staffing.models.EventDateLabel":{create_table:[11,3,1,""],get:[11,3,1,""]},"staffing.models.Job":{create_table:[11,3,1,""],filled:[11,3,1,""]},"staffing.models.JobRole":{create_table:[11,3,1,""]},"staffing.models.Location":{create_table:[11,3,1,""]},"staffing.models.StaffNotification":{create_table:[11,3,1,""]},"staffing.models.Task":{create_table:[11,3,1,""]},"staffing.models.UserJob":{"new":[11,3,1,""],create_table:[11,3,1,""],get_assigned_users:[11,3,1,""]},app:{get_db:[11,1,1,""],initalize_all_tables:[11,1,1,""],inject_site_config:[11,1,1,""]},shotglass2:{shotglass:[10,0,0,"-"]},staffing:{models:[11,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","method","Python method"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:method"},terms:{"00am":10,"00pm":10,"33am":10,"case":[0,3,5],"class":[10,11],"default":[0,2,3,5,10],"final":7,"function":[4,10],"import":10,"int":10,"new":[0,3,5,10,11],"public":[0,3,5,7],"return":[10,11],"static":10,"true":10,"try":10,"var":10,For:[0,3],NOT:3,The:[0,1,3,4,5,6,7,8,9,10,12],Then:0,There:[2,3,5],These:[0,3],_start_dat:11,abbr_date_str:10,abil:5,abl:[3,5,10],about:[0,2,3,4,5],abov:7,access:[4,8],accomplish:[0,7],account:[10,11],accur:5,across:3,activ:[3,4,7,10,11,12],activii:11,activitytyp:11,actual:[0,1,3,5,6],add:[0,3,5,7,10,11],add_rol:10,added:[5,10],addit:[0,3],address:[3,10],adhock:11,admin:[0,5,10,12],admin_list:10,administ:10,administr:[0,4,5],advoc:7,after:[3,5,10],again:[0,10],all:[0,4,5,7,10,11],allow:[3,7,10],alreadi:10,also:[0,3,5,10],alwai:[3,10],ani:[3,5,10],annual:0,anoth:3,anyon:7,app:[10,11],appear:[0,2,3,5,11],applic:7,area:7,arena:3,arg:10,around:[5,7],arriv:3,assess:10,assign:[3,11],associ:[0,3,5],assum:10,attach:10,attempt:10,attend:[3,4,5,11,12],authent:10,authenticate_us:10,automat:7,avail:7,awar:10,bake:0,base:[5,7,10,11],basic:[4,10],bcc:10,becaus:10,becom:0,been:11,befor:[0,3,10],being:10,below:3,bicycl:7,bike:[0,3],bit:0,blank:10,blind:10,blueprint:10,bodi:10,body_is_html:10,box:3,bring:5,broken:3,built:10,button:[3,5],calendar:[0,3,4,5,7,11,12],call:10,can:[0,3,5,7,10],cancel:3,carbon:10,categor:11,caus:3,chang:[3,5,10],check:[3,10],choos:3,chore:0,clean:0,clear:3,clear_rol:10,click:[0,2,3,5],client:[3,11],close:3,code:[7,11],column:10,com:7,come:2,commit:10,compil:10,complain:10,complet:10,config:10,conflict:10,connect:[10,11],contact:[3,10],contain:[7,10,11],content:10,context:[10,11],control:8,conveni:10,convert:10,coordin:5,copi:10,core:10,correspond:5,could:10,cours:0,cover:5,creat:[2,4,7,10,11],create_t:[10,11],cumbersom:0,current:[3,10,11],cursor:10,dai:0,databas:11,date:[0,3,5,7,11],date_to_str:10,date_util:10,datestr:10,datetim:10,datetime_as_str:10,db_connect:[10,11],decor:10,defin:[10,11],definit:10,delet:10,depric:10,describ:[3,4],descript:[0,3,5],design:[7,8],detail:[2,3,7],develop:[9,12],dialog:3,dict:11,dictionari:10,did:[5,10],differ:[3,5],directli:[3,10],directori:10,displai:[0,3,10],display_nam:10,doc:9,doe:11,doing:3,don:[10,11],done:7,door:3,down:3,drop:3,duplic:3,dure:[0,3,7],each:[0,3,5,7],earli:3,easier:0,edit:4,effect:10,either:[3,10],eleg:5,element:10,elig:8,els:10,email:[5,10],email_admin:10,empti:10,encod:10,encourag:3,end:[3,5,7,10,11],enter:[3,5],etc:0,event:[0,2,4,5,6,7,11,12],eventdatelabel:11,ever:0,exampl:[0,3,5],exclud:[3,10],exist:[0,3,5,10,11],expir:10,extend:11,extens:10,face:[0,3,5],fact:5,fail:10,fals:10,few:[0,3,10],field:[0,3,10,11],file:10,filenam:10,filespec:[10,11],fill:11,find:[0,2,3,5,10],first:10,flask:10,focus:[],folk:[3,5],follow:7,forget:10,form:[5,10],format:10,found:10,free:7,friend:5,friendli:11,from:[0,3,5,10],from_address:10,from_send:10,full:10,futur:5,gener:[3,10],get:[2,7,10,11],get_app_config:10,get_assigned_us:11,get_by_username_or_email:10,get_column_nam:10,get_contact_email:10,get_db:11,get_default_rout:10,get_rol:10,get_site_config:10,get_time_zone_set:10,get_with_rol:10,getdatetimefromstr:10,getpasswordhash:10,github:7,give:[0,3,5],global:10,goal:0,good:[0,5],group:[0,11],halloween:0,hand:3,handl:10,happen:[0,3,7],happi:0,has:[5,10,11],has_access:10,has_user_table_access:10,hash:10,have:[0,2,3,5,7,10],header:3,heat:5,held:3,help:[0,3,5,7,12],helper:10,here:[2,3,4,9,10,11],hide:[2,3],hierarch:5,hierarchi:7,higest:10,high:7,higher:5,hoc:11,hopefulli:3,host:10,hour:[1,5],how:[4,7,12],html:10,html_templat:10,http:7,hyperlink:10,idea:3,imag:10,inact:10,includ:[7,10,11],include_inact:10,index:12,indic:[7,10],info:[0,3,5],inform:[0,3,5],init:10,init_db:10,init_event_db:11,init_t:10,initalize_all_t:11,initalize_user_t:10,initi:[7,10,11],initialz:11,inject_site_config:11,inmutablemultidict:10,insert:10,instanc:10,instanci:10,instead:3,instruct:[0,3,7],integ:10,interact:10,interest:9,intern:0,intial:[10,11],is_admin:10,iso_date_str:10,item:[0,2,7,10],jinja_filt:10,jinja_load:10,job:[1,3,4,7,8,11,12],job_id:11,jobrol:11,jump:[0,1,3,5,6,8],just:[0,3,5,10],keep:[0,3],kind:3,know:[0,3],kwarg:[10,11],label:[3,11],label_or_id:11,land:2,last_access:10,leas:5,least:[7,10],leav:3,left:3,less:0,level:7,like:[0,3,5,10],limit:[5,10],link:[0,2,3,7],list:[3,5,10],load:10,local:10,local_date_and_time_str:10,local_date_str:10,local_datetime_now:10,local_time_str:10,locat:[3,4,5,11,12],log:[4,5],login_on_success:10,long_date_str:10,lot:[3,10],mai:[0,3,5,7,10],mail:10,mail_default_addr:10,mail_default_send:10,main:0,make:[0,3,5,10,11],make_db_path:10,make_tz_awar:10,manag:12,mani:[0,5,7],mar:10,march:10,mark:3,markdown:[3,5],match:10,matchpasswordtohash:10,max_role_rank:10,meaning:0,meant:2,member:[0,3],menu:[0,10],messag:10,method:10,might:0,minimum:[],minimum_rank_requir:10,model:[10,11],modifi:10,modul:[9,10,12],moment:5,mon:10,monthli:0,more:[0,2,3,5,7,10],most:5,move:3,mulipl:10,must:[0,5],name:[0,3,5,10],namedlist:[10,11],nameoremail:10,natur:3,need:[0,3,5,7,10,11],neither:10,never:10,next:5,no_commit:10,non:7,none:[10,11],nor:10,normal:10,note:10,notif:[3,11],now:[0,3,10],nowstr:10,number:[5,11],obj:10,object:10,occasion:0,occur:6,onc:3,one:[0,5,7,10],onli:[0,3,5,10],open:[0,3,7,10],opportun:5,option:[2,5,10],order:5,organ:[0,7],origin:3,other:[3,7,10],our:3,out:[2,10],output:10,over:0,overview:[4,12],own:10,packag:10,page:[0,2,3,5,12],pai:5,paid:[5,7],param:10,paramet:10,park:3,part:8,parti:0,particular:11,pass:10,passhash:10,path:[10,11],patrick:0,pend:3,peopl:[2,3,5,7,10],per:10,perform:[3,10],permiss:10,place:[0,3,6,10,11],plain:10,png:10,point:3,posit:11,possibl:[5,10],potenti:10,practic:7,prepend:10,present:[3,5],previou:10,primari:3,primarili:[0,7],privat:3,probabl:[0,3],profil:5,profit:7,project:[7,10],provid:[0,3,10],publicli:2,purpos:[0,3],put:[0,11],python:[7,10],queri:10,query_on:10,quick:10,quickli:3,quite_test_fixtur:10,random:10,rank:[5,10],rather:[3,10],read:[3,10],readi:3,realli:[0,10],reason:5,rec:10,rec_id:10,receiv:[5,10],recipi:10,record:[2,4,7,10,11,12],recover_password:10,recur:0,refer:[3,5],regist:10,register_www:10,registr:10,relat:0,remov:[],render:10,render_markdown:10,repeat:3,replac:10,repli:10,reply_to_address:10,reply_to_nam:10,replyto:10,report:0,repres:[0,3,6,10],request:5,requir:[4,5,11],reset:10,respons:10,restrict:5,result:[10,11],rich:[3,5],ride:0,role:[4,5,10,11,12],role_list:10,role_nam:10,roster:[0,3],rout:10,row:10,row_data:10,row_list:10,rows_to_namedlist:10,run:0,sacramento:7,safe:10,sale:0,same:[3,5,10],save:[3,10],save_table_search:10,schedul:3,scratch:3,script:10,search:[5,10,12],section:[3,4],see:[3,7,10],seen:3,select:[0,3,5,10,11],select_on:10,select_one_raw:10,select_raw:10,self:10,send:[10,11],send_messag:10,sender:10,sent:[3,10,11],serv:3,server:10,servic:[3,11],sesstion:10,set:[3,5,10,11],set_default:10,set_template_dir:10,setup:11,sever:0,shift:7,short_abbr_date_str:10,short_date_str:10,short_day_and_date_and_time_str:10,short_day_and_date_str:10,shortcut:10,shotglass2:[9,11],should:0,show:3,shuffl:5,sign:[3,5,8,10],signup:[2,3,11],silent_login:10,simpl:10,simplifi:10,singl:10,sit_config:10,site:[0,2,3,7,8,10,11,12],site_config:[10,11],skill:5,slot:5,softwar:9,some:[3,4,10],someth:[3,5],sourc:7,special:[0,10],specif:[3,7,11],specifi:[3,5,10],spread:3,sql:10,sqlite3:10,sqlitet:[10,11],staf:[4,9],staff:[0,3,5,7],staffnotif:11,start:[3,5,7],startup:10,statement:10,statu:3,step:4,still:3,store:10,str:10,stratagi:4,string:10,strip:10,style:0,subdomain:10,subject:10,subject_prefix:10,substitut:10,succeed:10,success:10,sure:10,syntax:[3,5],system:[5,7],tab:10,tablel:10,tableobj:10,take:[0,3,7,10],takeabeltof:[10,11],talk:0,task:[7,11],technic:12,templat:11,template_list:10,test:10,text:10,text_templ:10,than:[3,5,10],the_datetim:10,thei:[2,3,5,10],them:[0,3,5],themselv:0,therefor:3,thesalt:10,thi:[0,3,4,5,10,11],thier:10,thing:[3,7],this_app:10,those:0,though:[0,2],thought:[0,10],time:[0,3,5,7,10],time_zon:10,timesaround:10,timestamp:10,titl:[0,3,5],tld:10,to_address_list:10,togeth:0,top:5,track:5,train:0,trim:10,trim_str:10,tupl:10,turn:10,twice:11,type:[0,3,5],unchang:3,under:[0,11],unimport:10,unless:10,updat:[0,5,10],update_last_access:10,upon:10,url:10,use:[0,2,3,5,7,10],used:[0,1,3,5,8,10,11],useful:3,user:[1,4,8,11],user_has_rol:10,user_id:10,user_job:11,user_nam:10,user_rol:10,userid:10,userjob:11,usernam:10,userrol:10,using:[5,10],usual:3,utf:10,valet:3,valid:10,valu:[0,10],variou:8,veri:5,version:10,view:[0,3,5],viewabl:2,visit:[],visitor:[0,2,3,5,7],volunt:[2,3,5,7],wai:[0,7,10],want:[0,3,5,7,10],web:[0,2,3,4,7,8,10],weblink:10,well:[0,3],what:[0,2,3,5,7],when:[0,2,3,5,10],where:[3,6],which:[3,5,7,8,10],who:[2,3,5,10],window:10,wish:[2,5],within:0,without:5,wleddi:7,word:3,work:[1,3,5,10],would:[3,5],write:10,www:10,year:0,you:[0,2,3,5,7,10],your:[0,2,3,5,7,10],yyyi:10,zone:10},titles:["How to manage Activity records","How to manage Attendance Records","The Calendar","How to manage Event records","Managing the Site","How to manage Job records","How to Manage Location Records","Overview","How to manage Role Records","Technical Documentation","Shotglass2 Docs","Staffing Module","Welcome to Staffing\u2019s documentation!"],titleterms:{The:2,about:7,access:10,activ:0,administr:10,applic:11,assign:5,assignin:[],attend:1,basic:7,calendar:2,control:10,copi:3,creat:[0,1,3,5,6,8],data:10,databas:10,date:10,detail:0,doc:10,document:[9,12],edit:[0,1,3,5,6,8],event:3,filter:10,gener:0,how:[0,1,3,5,6,8],indic:12,jinja2:10,job:5,list:0,locat:6,login:10,mailer:10,manag:[0,1,3,4,5,6,8],modul:11,next:[0,3],open:5,overview:7,part:3,password:10,past:5,pref:10,process:10,record:[0,1,3,5,6,8],remov:5,role:8,root:11,shotglass2:10,shotglass:10,singl:0,site:4,some:0,specif:0,staf:[7,11,12],step:[0,3,7],storag:10,stratagi:0,tabl:[10,11,12],technic:9,templat:10,user:[5,10],util:10,veri:0,view:10,welcom:12,why:5}})