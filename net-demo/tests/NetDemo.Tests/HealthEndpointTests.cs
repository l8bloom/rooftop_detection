using System.Net;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;

namespace NetDemo.Tests
{
    public class HealthEndpointTests
    {
        private readonly HttpClient _client;

        public HealthEndpointTests()
        {
            var factory = new WebApplicationFactory<Program>();
            _client = factory.CreateClient();
        }

        [Fact]
        public async Task GetHealth_ReturnsHealthy()
        {
            var response = await _client.GetAsync("/health");
            response.EnsureSuccessStatusCode();
            Assert.Equal("application/json", response.Content.Headers.ContentType.MediaType);
            var json = await response.Content.ReadFromJsonAsync<HealthResponse>();
            Assert.NotNull(json);
            Assert.Equal("healthy", json!.Status);
        }

        [Fact]
        public async Task GetRoot_ReturnsNotFound()
        {
            var response = await _client.GetAsync("/");
            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        }

        private class HealthResponse
        {
            public string Status { get; set; } = "";
        }
    }
}
