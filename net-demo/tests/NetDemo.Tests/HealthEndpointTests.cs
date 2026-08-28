using System.Net;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

public class HealthEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public HealthEndpointTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task HealthEndpoint_ReturnsHealthy()
    {
        var client = _factory.CreateClient();
        var response = await client.GetAsync("/health");
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadFromJsonAsync<dynamic>();
        Assert.Equal("healthy", (string)json.status);
    }
}
