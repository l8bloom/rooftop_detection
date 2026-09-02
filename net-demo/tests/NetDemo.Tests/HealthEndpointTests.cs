using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;
using NetDemo;

public class HealthEndpointTests
{
    [Fact]
    public async Task GetHealth_ReturnsHealthy()
    {
        await using var factory = new WebApplicationFactory<Program>();
        var client = factory.CreateClient();
        var response = await client.GetAsync("/health");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadFromJsonAsync<HealthResponse>();
        Assert.NotNull(content);
        Assert.Equal("healthy", content?.Status);
    }
}

public record HealthResponse(string Status);
