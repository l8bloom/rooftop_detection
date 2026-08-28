# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj tests/NetDemo.Tests/
COPY src/NetDemo/*.cs src/NetDemo/
COPY tests/NetDemo.Tests/*.cs tests/NetDemo.Tests/
RUN dotnet restore NetDemo.sln
RUN dotnet publish NetDemo.sln -c Release -o /app/publish /p:PublishTrimmed=true
# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "NetDemo.dll"]
