using System.Net;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace NetDemo.Tests
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
            var content = await response.Content.ReadFromJsonAsync<HealthResponse>();
            Assert.NotNull(content);
            Assert.Equal("healthy", content.Status);
        }
    }

    public class HealthResponse
    {
        public string Status { get; set; } = string.Empty;
    }
}
