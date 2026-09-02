FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj tests/NetDemo.Tests/
RUN dotnet restore
COPY src/NetDemo/ src/NetDemo/
COPY tests/NetDemo.Tests/ tests/NetDemo.Tests/
RUN dotnet publish NetDemo.sln -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
# Run as non-root user
ARG APP_UID=1000
RUN adduser --uid ${APP_UID} --disabled-password --gecos '' appuser
USER appuser
ENTRYPOINT ["dotnet", "NetDemo.dll"]
