using System.Net.Http.Json;
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;

public class HealthEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public HealthEndpointTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task HealthEndpoint_ReturnsHealthy()
    {
        var response = await _client.GetAsync("/health");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadFromJsonAsync<HealthResponse>();
        Assert.Equal("healthy", content.status);
    }

    private class HealthResponse
    {
        public string status { get; set; } = null!;
    }
}
