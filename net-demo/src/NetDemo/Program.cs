using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);
        var app = builder.Build();
        app.MapGet("/health", () => Results.Json(new { status = "healthy" }));
        app.Run();
    }
}
