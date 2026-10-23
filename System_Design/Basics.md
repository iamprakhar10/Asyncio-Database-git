##### Signed URLs
In our public pulse we didn't used signed URLs. For the Pricvate S3 backup bucket, the EC2 accessed S3 using AWS credentials from it's IAM role, not through presigned/signed URL

A signed URL is basically:
A normal URL plus cryptographic proof saying, “whoever has this URL is allowed to perform this specific action for a limited time.”

For example, imagine this S3 object is private:
s3://my-private-bucket/report.pdf

Normally, if someone opens:
https://my-private-bucket.s3.amazonaws.com/report.pdf

AWS says:
Access Denied

because the object is private.

But your backend can generate a presigned URL like:
https://my-private-bucket.s3.amazonaws.com/report.pdf
    ?X-Amz-Expires=900
    &X-Amz-Signature=abc123...
    &...

That URL might mean:
Permission:
GET this specific object

Valid for:
15 minutes

Authenticated by:
cryptographic signature

So AWS can verify:
Incoming request
      ↓
Which object?
      ↓
Which HTTP action?  GET / PUT?
      ↓
Has URL expired?
      ↓
Is signature valid?
      ↓
YES
      ↓
Allow access

The main problem it solves is this:

Suppose your user needs to download a private file.

Without signed URLs, you might do:
User
  ↓
Your FastAPI server
  ↓
FastAPI downloads file from S3
  ↓
FastAPI sends file to user

That means your server becomes a middleman for potentially huge files.
It will also avoid us giving our AWS credentials to users

Backend has AWS permission
        ↓
creates temporary signed URL
        ↓
frontend gets only temporary permission


The signature is important because without it, someone could simply change:
/report-123.pdf

to:
/report-999.pdf

Backend has AWS credentials
        ↓
Backend creates a signature from:

HTTP method
object path
expiry time
timestamp
credential identity
other request details
        ↓
Backend puts that signature into the URL