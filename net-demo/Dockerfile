# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY net-demo.sln ./
COPY src/NetDemo/NetDemo.csproj ./src/NetDemo/
COPY src/NetDemo/Program.cs ./src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj ./tests/NetDemo.Tests/
COPY tests/NetDemo.Tests/HealthEndpointTests.cs ./tests/NetDemo.Tests/
RUN dotnet restore net-demo.sln
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS="http://+:8080"
EXPOSE 8080
# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser
ENTRYPOINT ["dotnet", "NetDemo.dll"]
