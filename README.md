# UCL - ELEC0138_ assignment

UCL ELEC0138 course final assignment by TEAM 3

The tutorial video link is : https://youtu.be/KSkep858Z9w

Group Member : Fu Siyi, Xu Mujie, Liu Yusen, Veerapatra Lilitwong
student number: 22079028, 19027325, 22081179, 22115386

Our coursework aims to build a secure website application, a messaging system.
In our blog or message website, we have implemented features for registering, 
modifying, and deleting messages, as well as basic login and registration functionality. Additionally, we have included an administrator portal for managing users and user messages.

The threat models we considered are the XSS and CSRF models, but this website can also defence 
against other threats, such as robot registrations and unauthorized access.

-- First step, user needs to register with email, name, self-defined password, and user needs
to manually enter the CAPTCHA and email verification code.

-- Second step, after registering successfully, user can login.

-- Third step, after entering the message board index page, user can sent comments.

    No special characters such as,< > , " , ' , % , ; , (), & , + , etc.
    
    Intergers should between 0-9
 
    Link is also forbiddened

-- User need to logout at the end

-- For admin login, 
    
    username: admin
    
    password: a@123456

-- Admin can manage the user list and the message list
    
    deleting the user, change their password

    deleting the messages





