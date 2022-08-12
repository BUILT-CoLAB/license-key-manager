using System;
using System.Net.Http;
using System.Threading.Tasks;
using LMlib;

namespace SampleClient
{
    class SampleClass
    {

        static void Main(string[] args)
        {
            var pubkey = @"<RSAKeyValue><Modulus>6rS3LTgnh9quJ+AdiHjMSHG2KXh6Li5cPId1XSElia1WOS4j0jNLScSGVS28naD6254YCZqkN8zdGt62RlAYdAErrcaYR5dbhIJ91uiKI/7yucr8TA8l2Pao7XRCqWNeqhsakoiATHye9Xvqsoo6sN8EaVACrIl7Cd0w1UlWowVw9cxXZO5qj2ebUhpJqS7+g4c2cx1fhmI9Kl4dZvidiJCIMJNxHMZL80ZcxftalR8xuuNnnvScbv84twhmh2NXeelK7rddVj9ZJfs2MIWtReGxJyjrd9pdkn0xUCIlqlTswB/+BLR8kznAbXkvSyNnyS9PHt9LyAGzRiJXuiaLqw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>";

            var api_key = "3ebec076-b65f-4e5d-bc3a-27846b13bffb";

            var serial = "9XAG0-OMRZ8-ZYZPT-5AHYO";

            var hostname = "https://slm.localhossadt.direct/";

            LicenseManager lm = new LicenseManager(pubkey, api_key, serial, hostname);
            Task<string> task = lm.validate();
            try
            {
                task.Wait();
                Console.WriteLine(task.Result);
            }
            catch (AggregateException ae)
            {
                ae.Handle((x) =>
                {
                    if (x is HttpRequestException) // This we know how to handle.
                    {
                        Console.WriteLine("{0} Exception caught in HTTP Request.", x.InnerException.Message);
                        return true;
                    }
                    return false; // Let anything else stop the application.
                });
            }

            catch (Exception e)
            {
                Console.WriteLine("{0} Exception caught.", e.InnerException.Message);
            }

        }
    }
}