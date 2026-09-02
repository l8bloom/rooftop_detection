# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj ./src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj ./tests/NetDemo.Tests/
RUN dotnet restore
COPY . .
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o out

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/out .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "NetDemo.dll"]
