# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY net-demo/ .
RUN dotnet restore NetDemo.sln
RUN dotnet publish NetDemo.sln -c Release -o out
# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/out .
EXPOSE 8080
# Run as non-root user specified by APP_UID
ARG APP_UID=1000
USER $APP_UID
ENTRYPOINT ["dotnet", "NetDemo.dll"]
