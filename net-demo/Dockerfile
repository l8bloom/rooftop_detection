# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj src/NetDemo/
RUN dotnet restore
COPY . .
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o /app/publish /p:PublishTrimmed=false
# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
ARG APP_UID=1000
RUN addgroup --gid ${APP_UID} appgroup && adduser --disabled-password --gecos "" --uid ${APP_UID} --gid ${APP_UID} appuser
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
USER appuser
ENTRYPOINT ["dotnet", "NetDemo.dll"]
