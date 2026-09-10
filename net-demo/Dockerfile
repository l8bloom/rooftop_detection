# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o /app --no-restore
# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .
ARG APP_UID=1000
USER $APP_UID
EXPOSE 8080
ENTRYPOINT ["dotnet","NetDemo.dll"]
