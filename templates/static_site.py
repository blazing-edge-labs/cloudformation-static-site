from troposphere import GetAtt, Join, Output
from troposphere import Parameter, Ref, Template
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget
from troposphere.s3 import BucketPolicy, WebsiteConfiguration
from troposphere.s3 import Bucket
from troposphere.s3 import CorsConfiguration, CorsRules
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import S3Origin, ForwardedValues
from troposphere.cloudfront import Origin, DefaultCacheBehavior


t = Template()

t.add_description(
    "AWS CloudFormation Template to create needed resources for static site "
    "hosting using s3, cloudfront and route53.  It assumes that "
    "you already  have a Hosted Zone registered with Amazon Route 53. "
)

HostedZoneName = t.add_parameter(Parameter(
    "HostedZoneName",
    Description="The DNS name of an existing Amazon Route 53 hosted zone",
    Type="String"
))

HostedZoneId = t.add_parameter(Parameter(
    "HostedZoneId",
    Description="Id of hosted zone",
    Type="String",
    # default value is for cloudfront
    Default="Z2FDTNDATAQYW2"
))

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
    WebsiteConfiguration=WebsiteConfiguration(
        IndexDocument="index.html"
    )
))

StaticSiteBucketDistribution = t.add_resource(Distribution(
    "StaticSiteBucketDistribution",
    DistributionConfig=DistributionConfig(
        Aliases=[
            Ref(HostedZoneName),
            Join("", ["www.", Ref(HostedZoneName)])
        ],
        DefaultCacheBehavior=DefaultCacheBehavior(
            TargetOriginId="staticBucketOrigin",
            ViewerProtocolPolicy="allow-all",
            ForwardedValues=ForwardedValues(QueryString=False)
        ),
        DefaultRootObject="index.html",
        Origins=[Origin(
            Id="staticBucketOrigin",
            DomainName=GetAtt(StaticSiteBucket, "DomainName"),
            S3OriginConfig=S3Origin(),
        )],
        Enabled=True,
        PriceClass="PriceClass_100"
    )
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

StaticSiteDNSRecord = t.add_resource(RecordSetGroup(
    "StaticSiteDNSRecord",
    HostedZoneName=Join("", [Ref(HostedZoneName), "."]),
    Comment="Records for the root of the hosted zone",
    RecordSets=[
        RecordSet(
            Name=Join("", [Ref(HostedZoneName), "."]),
            Type="A",
            AliasTarget=AliasTarget(
                Ref(HostedZoneId),
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
                Ref(HostedZoneId),
                Join(
                    "",
                    [GetAtt(StaticSiteBucketDistribution, "DomainName"), "."]
                ),
            )
        ),
    ],
))

t.add_output(Output(
    "CloudfrontDomainName",
    Description="Cloudfront domain name",
    Value=GetAtt(StaticSiteBucketDistribution, "DomainName")
))

t.add_output(Output(
    "S3WebsiteURL",
    Description="S3 Website URL",
    Value=GetAtt(StaticSiteBucket, "WebsiteURL")
))


def get():
    return t.to_json()
