## Running a Python function with GDAL and Pillow dependencies on Lambda ##
It's difficult, but not impossible to utilize GDAL and Pillow from Lambda. I found a few different resources online that helped me greatly, but didn't quite get me all of the way there. Below are the steps I used after combining instructions from other sites and trial and error on my own part. 

Resources I used:
* http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html
* https://github.com/vincentsarago/lambda_gdal-python

### Package Creation ###
Creating the package is a difficult process due to the GDAL dependencies.

1. Start a new EC2 instance using an Amazon Linux AMI. It is important that you choose an Amazon Linux AMI because the packages need to be built in the same OS that they will be used by Lambda.
    * Create at least a t2.small if not bigger. It will take awhile to build GDAL from source.
    * Make sure you add a SSH security group to the instance before you launch it.
    * Make sure you add it to a VPC with appropriate inbound/outbound route rules. 
    * Make sure you add your SSH key pair to the instance. This will allow you to SSH to it.
    * Start the instance.
1. Modify your SSH config file to allow you to SSH to the EC2 instance.
1. SSH to your EC2 instance.
1. Update and install Python
  
    ```
    sudo yum update
    sudo yum install python27-devel python27-pip gcc libjpeg-devel zlib-devel gcc-c++ python-devel libpng-devel freetype-devel libcurl-devel
    ```
1. Create a working directory and change to it.

    ```
    mkdir /home/ec2-user/lambda
    mkdir /home/ec2-user/lambda/local
    cd /home/ec2-user/lambda
    ```
1. Create a virtualenv and activate it.
   
    ```
    virtualenv lambda
    source lambda/bin/activate
    ```
1. Install numpy in your virtualenv
   
    ```
    pip --no-cache-dir install numpy
    ```
1. Install Pillow into your virtualenv
 
    ```
    pip install Pillow
    ```
1. Download and install proj.4 and GDAL from source (warning, this takes a long time to run)
    
    ```
    wget https://github.com/OSGEO/proj.4/archive/4.9.2.tar.gz
    tar -zvxf 4.9.2.tar.gz
    cd proj.4-4.9.2/
    ./configure --prefix=/home/ec2-user/lambda/local
    make
    make install
    
    cd ..
    
    wget http://download.osgeo.org/gdal/2.1.0/gdal-2.1.0.tar.gz
    tar -zxvf gdal-2.1.0.tar.gz
    cd gdal-2.1.0
    ./configure --prefix=/home/ec2-user/lambda/local --with-geos --with-static-proj4=/home/ec2-user/lambda/local --with-curl --with-python
    make
    make install
    
    cd ..
    ```
1. Install GDAL into your virtual environment - make sure you are still inside your virtual environment

    ```
    cd /home/ec2-user/lambda/gdal-2.1.0/swig/python
    python setup.py install
    
    # Verify that gdal is installed by running:
    pip freeze
    ```
1. Create an archive with the dependencies

    ```
    cd $VIRTUAL_ENV/lib64/python2.7/site-packages/GDAL-2.1.0-py2.7-linux-x86_64.egg
    
    # Move OSGEO and GDAL items into site-packages
    mv o* ../
    mv g* ../
    
    cd /home/ec2-user/lambda
    
    sudo cp local/lib/libgdal.so local/lib/libgdal.so.20
    zip -9 lambda.zip local/lib/libgdal.so.20
    zip -r9 lambda.zip local/lib/libproj.so.9
    sudo cp /usr/lib64/libjpeg.so.62 local/lib/libjpeg.so.8
    zip -r9 lambda.zip local/lib/libjpeg.so.8
    zip -r9 lambda.zip local/share
    cd $VIRTUAL_ENV/lib64/python2.7/site-packages
    zip -r9 /home/ec2-user/lambda/lambda.zip *
    
    # To verify contents of the zip
    cd /home/ec2-user/lambda
    less lambda.zip
    ```
1. Move the archive off of the EC2 instance using any method you are comfortable with - below uses AWS CLI to move it to a S3 bucket

    ```
    aws configure
    # copy/paste your AWS Access Key when prompted
    # copy/paste your AWS Secret Access Key when prompted
    # add your Default Region Name
    # set your preferred Default Output Format
    aws s3 cp lambda.zip s3://{S3 Bucket Name}/temp_lambda.zip
    ```
1. Terminate or stop the EC2 instance that you used to create the zip
1. Add Lambda function code to the root of the zip. This will be your handler and your worker. I added a basic stub handler and worker to this project that demonstrates how the Lambda function invokes the worker with GDAL libraries. [Here](http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html) is another good example of calling a worker from a lambda function and adding the dependencies to the library path.
1. Please make note of how I'm using a subprocess to shell out gdal in a different Python script and how I'm setting the LD_LIBRARY_PATH and PATH. I had to do it this way because if I had it all in one script, the Lambda was unable to find gdal on the path. For some reason, setting LD_LIBRARY_PATH as an environment variable is not respected unless you shell it out.


