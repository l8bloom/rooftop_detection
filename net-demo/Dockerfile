# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj src/NetDemo/NetDemo.csproj
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj tests/NetDemo.Tests/NetDemo.Tests.csproj
RUN dotnet restore NetDemo.sln
COPY . .
RUN dotnet publish NetDemo.sln -c Release -o /app/publish --no-restore

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser
CMD ["dotnet", "NetDemo.dll"]
