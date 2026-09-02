# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY src/NetDemo/NetDemo.csproj ./src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj ./tests/NetDemo.Tests/
COPY src/NetDemo/Program.cs ./src/NetDemo/
COPY src/NetDemo/NetDemo.csproj ./src/NetDemo/
COPY tests/NetDemo.Tests/HealthEndpointTests.cs ./tests/NetDemo.Tests/
RUN dotnet restore
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o out

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/out .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
USER app
ENTRYPOINT ["dotnet", "NetDemo.dll"]
