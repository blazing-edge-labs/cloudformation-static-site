[![Build Status](https://travis-ci.org/EastCoastProduct/cloudformation-static-site.png)](https://travis-ci.org/EastCoastProduct/cloudformation-static-site)
# cloudformation-static-site
CloudFormation script to set up static site hosting on AWS with S3 and CloudFront

1. [What does it do?](#what_does_it_do)
2. [Steps to run the script](#steps_to run the script)
3. [Setting the Root Redirect](#setting the root redirect)
4. [Getting Your Files on S3](#getting your files on s3)

## What does it do?<a name="what_does_it_do"></a>

This is a CloudFormation script that helps you host a static website on S3. The root file is set to the index.html on that bucket, so your page will need to have index.html root file or you can update the scripts yourself.

The only thing you need to do is sync your static page directory in the S3 bucket with index.html as the root.

## Steps to Run the Script<a name="steps_to_run_the_script"></a>

1. The only manual step required is to create a hosted zone for your domain on Route53 if you aren't using Route53 for your site already. This is required to host a static page on AWS (__Important:__ Remember to transfer your existing DNS records to Route53)
2. Modify files in config as needed. You need to edit `config/config.yml`  and change the configuration values as needed. Configuration options are very self-explanatory
3. Install packages to run the script using pip install <package>
  1. _boto_ - and configure _boto_ with your AWS keys [Boto config](http://boto.readthedocs.org/en/latest/boto_config_tut.html)
  2. _troposphere_ - CloudFormation templates are written using _troposphere_ package
4. Finally, run the script `python cfn.py --create`
  * `-c` or `--create` is a flag to note that it's to create the stack and if you need to update it later due to some changes just leave that flag out
5. Optional: Manually change the static site configuration on S3 by following these [steps](#manual_origin)

That's it, you are now all set up to host a static site on AWS S3 and CloudFront. The only thing left to do is to transfer your files to the bucket.

## Setting the Root Redirect<a name="www_to_root"></a>

This option allows you to choose between having the root domain redirect to a www subdomain or vice versa. For example, if www_to_root is set to "True," requests to www.example.com will be redirected to example.com and if its set to "False" requests to example.com will be redirected to www.example.com.

Depending on the option selected, CloudFront will use different S3 buckets to serve the files. If set to "True" and the main domain is the root domain, it will use that S3 bucket (`example.com` bucket). If set to "False" and the www subdomain is the main one, it will use the `www.example.com` bucket to serve the files.

## Getting your Files on S3<a name="get_files_on_s3"></a>

Depending on how the www_to_root config optionis set up, files will need to be uploaded either to the `example.com` or `www.example.com` S3 bucket. You can upload files manually from the AWS console or through a script. If you don't have a script, we've written a gulp publish task to help you upload files to S3. Check it out at the [East Coast Product](https://github.com/EastCoastProduct/homepage) homepage.
