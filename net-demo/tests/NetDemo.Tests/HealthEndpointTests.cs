using System.Net;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace NetDemo.Tests;
{
    public class HealthEndpointTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly HttpClient _client;

        public HealthEndpointTests(WebApplicationFactory<Program> factory)
        {
            _client = factory.CreateClient();
        }

        [Fact]
        public async Task GetHealth_ReturnsHealthy()
        {
            var response = await _client.GetAsync("/health");
            response.EnsureSuccessStatusCode();
            var json = await response.Content.ReadFromJsonAsync<dynamic>();
            Assert.NotNull(json);
            Assert.Equal("healthy", (string)json.status);
        }

        [Fact]
        public async Task GetRoot_ReturnsNotFound()
        {
            var response = await _client.GetAsync("/");
            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        }
    }
}
