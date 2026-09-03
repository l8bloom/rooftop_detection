# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY src/NetDemo/NetDemo.csproj src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj tests/NetDemo.Tests/
COPY src/NetDemo/Program.cs src/NetDemo/
COPY tests/NetDemo.Tests/HealthEndpointTests.cs tests/NetDemo.Tests/
RUN dotnet restore src/NetDemo/NetDemo.csproj
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o /app/publish

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet","NetDemo.dll"]
