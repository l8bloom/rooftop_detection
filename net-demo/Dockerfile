# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY *.sln .
COPY src/NetDemo/*.csproj src/NetDemo/
COPY tests/NetDemo.Tests/*.csproj tests/NetDemo.Tests/
RUN dotnet restore
COPY . .
RUN dotnet publish src/NetDemo/NetDemo.csproj -c Release -o out

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/out .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
# Run as non-root user
ARG APP_UID=10001
RUN adduser --disabled-password --gecos "" --uid $APP_UID app && \
    chown -R app:app /app
USER app
ENTRYPOINT ["dotnet", "NetDemo.dll"]
