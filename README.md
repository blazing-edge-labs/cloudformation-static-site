[![Build Status](https://travis-ci.org/EastCoastProduct/cloudformation-static-site.png)](https://travis-ci.org/EastCoastProduct/cloudformation-static-site)
# cloudformation-static-site
CloudFormation script to set up static site hosting on AWS with S3 and CloudFront

1. [What does it do?](#what_does_it_do)
2. [Steps to make it work](#steps_to_make_it_work)
3. [www to root config](#www_to_root)
4. [get files on S3](#get_files_on_s3)
5. (optional) [manually set CDN origin to static website](#manual_origin)

## What does it do?<a name="what_does_it_do"></a>

This is the CloudFormation script that gets you up and running for hosting a static website on S3 and making it even faster behind CloudFront CDN. After CloudFormation stack is successfully created you are all set up on the AWS to host a static page. Root file is set to the index.html on that bucket, so your page will need to have index.html root file or you can update the scripts and change it to something else.

The only thing you need to do  is to sync your static page directory on s3 bucket with index.html as root.

## steps to make it work<a name="steps_to_make_it_work"></a>

1. only manual step required is to create a hosted zone for your domain on route53 if you don't use route53 for your site already. You will need to use it if you want to host a static page on AWS (__important:__ remember to transfer your existing DNS records to route53)
2. modify files in config per your need. You need to edit `config/config.yml` file and change configuration values to whatever you need yours to be. Configuration options are very self-explanatory
3. install packages needed for script to run using pip install <package>
  1. _boto_ - and configure _boto_ with your AWS keys [Boto config](http://boto.readthedocs.org/en/latest/boto_config_tut.html)
  2. _troposphere_ - CloudFormation templates are written using _troposphere_ package
4. that's it, just run the script `python cfn.py --create`
  * `-c` or `--create` is a flag to note that it's to create the stack and if you need to update it later due to some changes just leave that flag out
5. (optional) manually change static site configuration on S3 following the [steps](#manual_origin)

That's it, you are now all set up to host a static site on AWS S3 and CloudFront. The only thing left to do is to get your files in that bucket.

## www_to_root<a name="www_to_root"></a>

This option gives a choice to pick between having root domain redirect to www subdomain or vice versa. For example, if www_to_root is set to true requests to www.example.com will be redirected to example.com and if its set to false requests to example.com will be redirected to www.example.com.

Depending on which option is used CloudFront is set up to use different S3 bucket to serve files. If set true and main domain is root domain it's using that S3 bucket (`example.com` bucket).

If set false and www subdomain is main it's using `www.example.com` bucket to serve the files, so use buckets to upload files according to this setting.

## get_files_on_s3<a name="get_files_on_s3"></a>

As explained in www_to_root config option, depending on which way it is set up, files need to be uploaded either on `example.com` or `www.example.com` S3 bucket. You can get files up there in any way you want, manually uploading them from AWS console or doing that through some kind of script.

 I hope you won't do the uploading manually, so check our [homepage](https://github.com/EastCoastProduct/homepage) that has a gulp publish task for uploading files to s3.

## manually set origin to static website URL<a name="manual_origin"></a>

This is a limitation of CloudFormation as the return value from S3 bucket creation is WebsiteURL with included HTTP protocol and CloudFront requires origin to be without protocol. At this point it's impossible to automate this process so you need to do following steps to achieve this (benefit of this is that routing will work properly as well as 404 error pages).

1. Navigate to AWS console
2. Go to CloudFormation
2. Select your newly created distribution
3. Navigate to Origins
4. Add new origin using static URL without protocol (e.g. eastcoastproduct.com.s3-website-us-east-1.amazonaws.com)
5. Delete the old origin that was set up directly to S3 bucket
