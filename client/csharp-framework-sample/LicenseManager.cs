using System;
using System.Management;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http;
using System.Net;
using System.IO;

namespace LMlib
{
    class LicenseManager
    {

        private string _pubKey { get; set; }
        private string _apiKey { get; set; }
        private string _serialNumber { get; set; }
        private string _hostname { get; set; }
        private string _deviceUUID { get; set; }

        private static string _endpoint = "api/v1/validate";


        private string getCPUId()
        {

            StringBuilder cpuInfo = new StringBuilder();
            ManagementClass mc = new ManagementClass("win32_processor");
            ManagementObjectCollection moc = mc.GetInstances();

            foreach (ManagementObject mo in moc)
            {
                Object obj = mo.Properties["deviceId"].Value.ToString();
                cpuInfo.Append(Convert.ToString(obj));
                cpuInfo.Append('_');

                obj = mo.Properties["processorID"].Value.ToString();
                cpuInfo.Append(Convert.ToString(obj));
                cpuInfo.Append('_');

                obj = mo.Properties["SerialNumber"].Value.ToString();
                cpuInfo.Append(Convert.ToString(obj));
            }
            return cpuInfo.ToString().Replace(" ", string.Empty);
        }

        private static string Base64Encode(byte[] byteText)
        {
            return System.Convert.ToBase64String(byteText);
        }

        private byte[] Encrypt(string data)
        {
            RSACng rsaKey = new RSACng();
            rsaKey.FromXmlString(_pubKey);
            var dataToEncrypt = Encoding.UTF8.GetBytes(data);
            // max size payload = 190 bytes with 2048 key
            var encryptedByteArray = rsaKey.Encrypt(dataToEncrypt, RSAEncryptionPadding.OaepSHA256);
            return encryptedByteArray;

        }


        private string encryptPayload()
        {
            StringBuilder plainPayload = new StringBuilder();
            plainPayload.Append(Convert.ToString(_serialNumber));
            plainPayload.Append(':');
            plainPayload.Append(Convert.ToString(_deviceUUID));

            Console.WriteLine(plainPayload.ToString());
            var b64payload = Base64Encode(Encrypt(plainPayload.ToString()));

            return b64payload;
        }

        public async Task<string> ValidateAsync()
        {
            var client = new HttpClient();

            var options = new Newtonsoft.Json.Linq.JObject();
            options["apiKey"] = _apiKey;
            options["payload"] = encryptPayload();

            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri(_hostname + _endpoint),
                Content = new StringContent(options.ToString(), Encoding.UTF8, "application/json"),
            };
            var response = await client.SendAsync(request);
            response.EnsureSuccessStatusCode();
            var responseBody = await response.Content.ReadAsStringAsync();
            return responseBody.ToString();
        }

        public LicenseManager(string pub, string api, string serial, string hostname)
        {
            if (!RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                throw new NotSupportedException("This is a Windows-only library");
            }
            _pubKey = pub;
            _apiKey = api;
            _serialNumber = serial;
            _hostname = hostname;
            _deviceUUID = getCPUId();
        }

    }
}