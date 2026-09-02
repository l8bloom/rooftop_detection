# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY NetDemo.sln .
COPY src/ ./src/
COPY tests/ ./tests/
RUN dotnet restore
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o /publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
ENTRYPOINT ["dotnet", "NetDemo.dll"]
