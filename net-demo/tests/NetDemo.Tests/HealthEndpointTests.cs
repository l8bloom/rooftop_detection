using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

public class HealthEndpointTests
{
    [Fact]
    public async Task HealthEndpoint_ReturnsHealthy()
    {
        await using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();
        var response = await client.GetAsync("/health");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        Assert.Equal("{\"status\":\"healthy\"}", content);
        Assert.Equal("application/json", response.Content.Headers.ContentType.MediaType);
    }

    [Fact]
    public async Task RootEndpoint_ReturnsNotFound()
    {
        await using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();
        var response = await client.GetAsync("/");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
