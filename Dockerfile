# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj tests/NetDemo.Tests/
RUN dotnet restore
COPY src/NetDemo/ src/NetDemo/
COPY tests/NetDemo.Tests/ tests/NetDemo.Tests/
RUN dotnet publish NetDemo.sln -c Release -o /app/publish
# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
# Run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
ENTRYPOINT ["dotnet","NetDemo.dll"]
