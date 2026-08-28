# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY NetDemo.sln ./
COPY src/NetDemo/NetDemo.csproj ./src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj ./tests/NetDemo.Tests/
COPY src/NetDemo/Program.cs ./src/NetDemo/
COPY tests/NetDemo.Tests/HealthEndpointTests.cs ./tests/NetDemo.Tests/
RUN dotnet restore NetDemo.sln
RUN dotnet publish NetDemo.sln -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
# Run as non-root user
ARG APP_UID=1000
RUN addgroup --gid ${APP_UID} appgroup && adduser --uid ${APP_UID} --gid ${APP_UID} --shell /bin/sh --disabled-password appuser
USER appuser
ENTRYPOINT ["dotnet", "NetDemo.dll"]
