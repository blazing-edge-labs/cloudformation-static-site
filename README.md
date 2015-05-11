# cloudformation-static-site [![Build Status](https://travis-ci.org/EastCoastProduct/cloudformation-static-site.png)](https://travis-ci.org/EastCoastProduct/cloudformation-static-site)
Cloudformation script to set up static site hosting on AWS with S3 and Cloudfront

1. [What does it do?](#what_does_it_do)
2. [Steps to make it work](#steps_to_make_it_work)
3. [www to root config](#www_to_root)
4. [get files on S3](#get_files_on_s3)

## What does it do?<a name="what_does_it_do"></a>

This is cloudformation script that gets you up and running for hosting a static website on S3 and making it even faster behind CloudFront. After cloudformation stack is successfully created you are all set up on AWS to host static page. Root file is set to index.html on that bucket, so your page will need to have index.html root file or you can update the scripts to change it.

Only thing you need to do  is to sync your static page directory on s3 bucket with index.html as root.

## steps to make it work<a name="steps_to_make_it_work"></a>

1. only manual step is to create hosted zone for your domain on route53 if you don't use route53 for your site already, you'll need to however if you want to achieve this (remember to transfer your existing DNS records to route53)
2. modify files in config, you need to put your domain in params.yml (hosted zone) and you can change stack name in config.yml as you'll probably want different stack name, when setting [www_to_root](#www_to_root) please see description below
3. install packages needed for script to run using pip install <package>
  1. boto - and configure boto with your aws keys [Boto config](http://boto.readthedocs.org/en/latest/boto_config_tut.html)
  2. troposphere - cloudformation templates are written in it
4. thats it, just run the script `python cfn.py --create`
  * `-c` or `--create` is a flag to note that its to create the stack and if you need to update it later for some changes just leave that flag out

Thats it, you are now all set up to host static site on AWS S3 and CloudFront. Only thing left to do is to get your files on that bucket.

## www_to_root<a name="www_to_root"></a>

This option gives a choice to pick between having root domain redirect to www subdomain or vice versa. For example if www_to_root is set to true requests to www.example.com will be redirected to example.com and if its set to false requests to example.com will be redirected to www.example.com.

Depending on which option is used CloudFront is set up to use different S3 bucket to serve files. If set to true and main domain is root domain its using that S3 bucket (example.com bucket).

If set to false and www subdomain is main its using www.example.com bucket to serve the files, so use buckets to upload files according to this settings.

## get_files_on_s3<a name="get_files_on_s3"></a>

As explained in www_to_root config option, depending on which way it is set up, files need to be uploaded either on example.com or www.example.com S3 bucket. You can get files up there in any way you want, manually uploading them from AWS console or doing that through some kind of script.

 I hope you won't do the uploading manually, so check the [static-site-bootstrap](https://github.com/EastCoastProduct/static-site-bootstrap) that has a gulp publish task that does the uploading files to s3 aswell as an example of nice static site structure to see an example of it.
