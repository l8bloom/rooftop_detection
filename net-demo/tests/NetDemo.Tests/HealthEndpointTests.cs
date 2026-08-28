using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

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
        Assert.Equal("application/json; charset=utf-8", response.Content.Headers.ContentType.ToString());
        var json = await response.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("healthy", json.GetProperty("status").GetString());
    }

    [Fact]
    public async Task Root_ReturnsNotFound()
    {
        var response = await _client.GetAsync("/");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
