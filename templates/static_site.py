from troposphere import GetAtt, Join, Output, FindInMap
from troposphere import Parameter, Ref, Template
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget
from troposphere.s3 import BucketPolicy, WebsiteConfiguration
from troposphere.s3 import Bucket, RedirectAllRequestsTo
from troposphere.s3 import CorsConfiguration, CorsRules
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import ForwardedValues, CustomOrigin
from troposphere.cloudfront import Origin, DefaultCacheBehavior
import yaml


t = Template()

text = open("config/config.yml", 'r')
config = yaml.load(text)
www_to_root = config['www_to_root']


t.add_description(
    "AWS CloudFormation Template to create needed resources for static site "
    "hosting using s3, cloudfront and route53.  It assumes that "
    "you already  have a Hosted Zone registered with Amazon Route 53. "
)

t.add_mapping('RegionMap', {
    "us-east-1": {
        "hostedzoneID": "Z3AQBSTGFYJSTF",
        "websiteendpoint": "s3-website-us-east-1.amazonaws.com"
    },
    "us-west-1": {
        "hostedzoneID": "Z2F56UZL2M1ACD",
        "websiteendpoint": "s3-website-us-west-1.amazonaws.com"
    },
    "us-west-2": {
        "hostedzoneID": "Z3BJ6K6RIION7M",
        "websiteendpoint": "s3-website-us-west-2.amazonaws.com"
    },
    "eu-west-1": {
        "hostedzoneID": "Z1BKCTXD74EZPE",
        "websiteendpoint": "s3-website-eu-west-1.amazonaws.com"
    },
    "ap-southeast-1": {
        "hostedzoneID": "Z3O0J2DXBE1FTB",
        "websiteendpoint": "s3-website-ap-southeast-1.amazonaws.com"
    },
    "ap-southeast-2": {
        "hostedzoneID": "Z1WCIGYICN2BYD",
        "websiteendpoint": "s3-website-ap-southeast-2.amazonaws.com"
    },
    "ap-northeast-1": {
        "hostedzoneID": "Z2M4EHUR26P7ZW",
        "websiteendpoint": "s3-website-ap-northeast-1.amazonaws.com"
    },
    "sa-east-1": {
        "hostedzoneID": "Z31GFT0UA1I2HV",
        "websiteendpoint": "s3-website-sa-east-1.amazonaws.com"
    },
    "cloudfront": {
        "hostedzoneID": "Z2FDTNDATAQYW2"
    }
})

HostedZoneName = t.add_parameter(Parameter(
    "HostedZoneName",
    Description="The DNS name of an existing Amazon Route 53 hosted zone",
    Type="String"
))

# prepare different configuration for www to root and vice versa
if www_to_root:
    print("Redirecting www to root domain.")
    aliases = [Ref(HostedZoneName)]
    bucket_website_conf = WebsiteConfiguration(IndexDocument="index.html")
    www_bucket_website_conf = WebsiteConfiguration(
        RedirectAllRequestsTo=RedirectAllRequestsTo(
            Protocol='http',
            HostName=Ref(HostedZoneName)
        )
    )

else:
    print("Redirecting root domain to www.")
    aliases = [Join("", ["www.", Ref(HostedZoneName)])]
    bucket_website_conf = WebsiteConfiguration(
        RedirectAllRequestsTo=RedirectAllRequestsTo(
            Protocol='http',
            HostName=Join("", ["www.", Ref(HostedZoneName)])
        )
    )
    www_bucket_website_conf = WebsiteConfiguration(IndexDocument="index.html")

StaticSiteBucket = t.add_resource(Bucket(
    "StaticSiteBucket",
    AccessControl="PublicRead",
    BucketName=Ref(HostedZoneName),
    CorsConfiguration=CorsConfiguration(
        CorsRules=[CorsRules(
            AllowedHeaders=["*"],
            AllowedMethods=["GET"],
            AllowedOrigins=["*"],
            ExposedHeaders=["Date"],
            MaxAge=3600
        )],
    ),
    WebsiteConfiguration=bucket_website_conf
))

wwwStaticSiteBucket = t.add_resource(Bucket(
    "wwwStaticSiteBucket",
    AccessControl="PublicRead",
    BucketName=Join("", ["www.", Ref(HostedZoneName)]),
    CorsConfiguration=CorsConfiguration(
        CorsRules=[CorsRules(
            AllowedHeaders=["*"],
            AllowedMethods=["GET"],
            AllowedOrigins=["*"],
            ExposedHeaders=["Date"],
            MaxAge=3600
        )],
    ),
    WebsiteConfiguration=www_bucket_website_conf
))

origin_static_url = "{0}.s3-website-{1}.amazonaws.com".format(
    config["params"]["HostedZoneName"], config["region_name"])
if not www_to_root:
    origin_static_url = "www.{0}".format(origin_static_url)

StaticSiteBucketDistribution = t.add_resource(Distribution(
    "StaticSiteBucketDistribution",
    DistributionConfig=DistributionConfig(
        Aliases=aliases,
        DefaultCacheBehavior=DefaultCacheBehavior(
            TargetOriginId="staticSiteBucketOrigin",
            ViewerProtocolPolicy="allow-all",
            ForwardedValues=ForwardedValues(QueryString=False)
        ),
        DefaultRootObject="index.html",
        Origins=[Origin(
            Id="staticSiteBucketOrigin",
            DomainName=origin_static_url,
            CustomOriginConfig=CustomOrigin(
                OriginProtocolPolicy="http-only"
            ),
        )],
        Enabled=True,
        PriceClass="PriceClass_100"
    ),
    DependsOn=["StaticSiteBucket", "wwwStaticSiteBucket"]
))

StaticSiteBucketPolicy = t.add_resource(BucketPolicy(
    "StaticSiteBucketPolicy",
    Bucket=Ref(StaticSiteBucket),
    PolicyDocument={
        "Statement": [{
            "Action": ["s3:GetObject"],
            "Effect": "Allow",
            "Resource": {
                "Fn::Join": ["", [
                    "arn:aws:s3:::",
                    {"Ref": "StaticSiteBucket"},
                    "/*"
                    ]
                ]},
            "Principal": "*"
            }]
    }
))

wwwStaticSiteBucketPolicy = t.add_resource(BucketPolicy(
    "wwwStaticSiteBucketPolicy",
    Bucket=Ref(wwwStaticSiteBucket),
    PolicyDocument={
        "Statement": [{
            "Action": ["s3:GetObject"],
            "Effect": "Allow",
            "Resource": {
                "Fn::Join": ["", [
                    "arn:aws:s3:::",
                    {"Ref": "wwwStaticSiteBucket"},
                    "/*"
                    ]
                ]},
            "Principal": "*"
            }]
    }
))

# prepares DNS records depending on redirect direction
if www_to_root:
    record_sets = [
        RecordSet(
            Name=Join("", [Ref(HostedZoneName), "."]),
            Type="A",
            AliasTarget=AliasTarget(
                FindInMap("RegionMap", "cloudfront", "hostedzoneID"),
                Join(
                    "",
                    [GetAtt(StaticSiteBucketDistribution, "DomainName"), "."]
                ),
            )
        ),
        RecordSet(
            Name=Join("", ["www.", Ref(HostedZoneName), "."]),
            Type="A",
            AliasTarget=AliasTarget(
                FindInMap("RegionMap", Ref("AWS::Region"), "hostedzoneID"),
                FindInMap("RegionMap", Ref("AWS::Region"), "websiteendpoint")
            )
        ),
    ]
else:
    record_sets = [
        RecordSet(
            Name=Join("", [Ref(HostedZoneName), "."]),
            Type="A",
            AliasTarget=AliasTarget(
                FindInMap("RegionMap", Ref("AWS::Region"), "hostedzoneID"),
                FindInMap("RegionMap", Ref("AWS::Region"), "websiteendpoint")
            )
        ),
        RecordSet(
            Name=Join("", ["www.", Ref(HostedZoneName), "."]),
            Type="CNAME",
            TTL="900",
            ResourceRecords=[
                GetAtt(StaticSiteBucketDistribution, "DomainName")
            ]
        ),
    ]

StaticSiteDNSRecord = t.add_resource(RecordSetGroup(
    "StaticSiteDNSRecord",
    HostedZoneName=Join("", [Ref(HostedZoneName), "."]),
    Comment="Records for the root of the hosted zone",
    RecordSets=record_sets
))

t.add_output(Output(
    "CloudfrontDomainName",
    Description="Cloudfront domain name",
    Value=GetAtt(StaticSiteBucketDistribution, "DomainName")
))

t.add_output(Output(
    "S3WebsiteURL",
    Description="S3 Website URL",
    Value=GetAtt(wwwStaticSiteBucket, "WebsiteURL")
))


def get():
    return t.to_json()
